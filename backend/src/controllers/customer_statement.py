# Python imports
from collections import defaultdict
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Any, List
import pytz

# Pip imports
from loguru import logger

# Internal imports
from src.controllers import orders as order_controller
from src.crud.account_crud import AccountCRUD
from src.crud.line_item_crud import LineItemCrud
from src.crud.order_crud import OrderCRUD
from src.database.models.orders.order import Order
from src.schemas.accounts import Account
from src.schemas.customer import CustomerDetail
from src.schemas.orders import FeeTransaction, OrderDetail, OrderTransaction, RentalStatementDataRequest
from src.schemas.rental_statement import ContainerInfo, RentHistory, RentInfo, RentalStatement, RentalStatementMultipleOrders
from src.services.payment.authorize_pay_service import get_customer_profile
from src.crud.single_customer_crud import single_customer_crud

order_crud = OrderCRUD()
linetitem_crud = LineItemCrud()
account_crud = AccountCRUD()


class CustomerStatement:
    def __init__(self) -> None:
        pass

    def generate_period_status(self, period):
        if period.calculated_rent_period_total_balance == 0:
            return "PAID"
        if (
            period.calculated_rent_period_total_balance != 0
            and period.transaction_type_rent_period is not None
            and len(period.transaction_type_rent_period) > 0
        ):
            return "PARTIALLY PAID"
        return "UNPAID"

    def generate_period_fee_status(self, period):
        if period.calculated_rent_period_fee_balance == 0:
            return "PAID"
        if (
            period.calculated_rent_period_fee_balance != 0
            and period.transaction_type_rent_period is not None
            and len(period.transaction_type_rent_period) > 0
        ):
            return "PARTIALLY PAID"
        return "UNPAID"

    def build_transaction_list(self, order: Order, periods_in_the_past) -> List[OrderTransaction]:
        transactions_list = []

        for period in order.rent_periods:
            order_transaction = OrderTransaction()
            order_transaction.fees = []
            order_transaction.date = str(period.start_date.strftime("%m/%d/%y")) if period.start_date else None 
            order_transaction.start_date = str(period.start_date.strftime("%m/%d/%y")) if period.start_date else None
            order_transaction.end_date = str(period.end_date.strftime("%m/%d/%y")) if period.end_date else None
            order_transaction.amount = period.amount_owed
            order_transaction.status = self.generate_period_status(period)
            try:
                order_transaction.tax = (
                    period.amount_owed
                    / (period.amount_owed + period.calculated_rent_period_fees)
                    * period.calculated_rent_period_tax
                )
            except:
                order_transaction.tax = 0
        
            order_transaction.description = 'RENT'
            combined_fees = defaultdict(
                lambda: {
                    "amount": Decimal("0.00"),
                    "tax": Decimal("0.00"),
                    "start_date": "00/00/00",
                    "end_date": "00/00/00",
                }
            )

            combined_transactions = defaultdict(
                lambda: {
                    "amount": Decimal("0.00"),
                    "date": "00/00/00",
                    "description": "Payment (method)",
                }
            )

            period.rent_period_fees.sort(key=lambda x: x.created_at, reverse=False)
            for fee in period.rent_period_fees:
                fee_tax = Decimal("0.00")
                if fee.type.is_taxable:
                    fee_tax = (
                        fee.fee_amount
                        / (period.amount_owed + period.calculated_rent_period_fees)
                        * period.calculated_rent_period_tax
                    )
                else:
                    fee_tax = Decimal("0")
                des = fee.type.name
                combined_fees[des]["amount"] += Decimal(fee.fee_amount)
                combined_fees[des]["tax"] += fee_tax
                if combined_fees[des]['start_date'] == '00/00/00':
                    combined_fees[des]["description"] = (
                        fee.type.display_name if fee.type.display_name is not None else fee.type.name
                    )
                    combined_fees[des]["start_date"] = str(datetime.strftime(fee.created_at, "%m/%d/%y"))
                    combined_fees[des]["end_date"] = str(datetime.strftime(fee.created_at, "%m/%d/%y"))
                else:
                    combined_fees[des]["end_date"] = str(datetime.strftime(fee.created_at, "%m/%d/%y"))

                if hasattr(combined_fees[des], 'status'):
                    if combined_fees[des]['status'] == 'PAID':
                        combined_fees[des]['status'] = self.generate_period_fee_status(period)
                else:
                    combined_fees[des]['status'] = self.generate_period_fee_status(period)

                if combined_fees[des]['start_date'] == combined_fees[des]["end_date"]:
                    combined_fees[des]["date"] = f"{combined_fees[des]['start_date']}"
                else:
                    combined_fees[des][
                        "date"
                    ] = f"{combined_fees[des]['start_date']} thru {combined_fees[des]['end_date']}"

                fee_transaction = FeeTransaction()
                if fee.type.name == 'DROP_OFF' or fee.type.name == 'PICK_UP':
                    fee_transaction.created_at = str(order.delivered_at)
                else:
                    fee_transaction.created_at = (
                        str(fee.due_at) if fee.due_at else str(fee.created_at.strftime("%m/%d/%y"))
                    )

                fee_transaction.amount = fee.fee_amount
                fee_transaction.status = self.generate_period_fee_status(period)
                fee_transaction.start_date = (
                    str(period.start_date) if period.start_date else None
                )
                fee_transaction.tax = fee_tax
                fee_transaction.description = (
                    fee.type.display_name if fee.type.display_name is not None else fee.type.name
                )
                fee_transaction.name = fee.type.name
                order_transaction.fees.append(fee_transaction)
            index = 0
            for transaction in period.transaction_type_rent_period:
                description = f"Payment - {transaction.payment_type}"
                combined_transactions[index]["amount"] = Decimal(transaction.amount)
                combined_transactions[index]["date"] = str(
                    transaction.transaction_effective_date.strftime("%m/%d/%y") if transaction.transaction_effective_date else None
                )
                combined_transactions[index]["description"] = description.upper()
                index += 1
            order_transaction.fees.sort(key=lambda x: x.start_date, reverse=False)

            order_transaction.concatenated_fees = combined_fees
            order_transaction.transaction_type_rent_period = combined_transactions
            transactions_list.append(order_transaction)
        transactions_list.sort(key=lambda x: x.start_date, reverse=False)
        return transactions_list

    def parse_date(self, date_str):
        for fmt in ("%m/%d/%y", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Date format not recognized: {date_str}")

    async def _get_base_rental_data(self, order_id: str, account_id: int):
        """Shared base method to get common rental data used by both PDF and web methods."""
        # Retrieve order and account
        order = None
        try:
            order: Order = await order_crud.get_one(order_id)
        except:
            return None
        account: Account = await account_crud.get_one(account_id)

        # Skip if not a rent order or no rent periods
        if order.type != 'RENT' or len(order.rent_periods) == 0:
            return None

        # Get customer info
        check_is_single_cust_dict = order_controller.check_is_single_customer_order(order=order)
        customer_info = check_is_single_cust_dict.get("customer_info", {})
        
        # Get company name
        company_name = account.cms_attributes.get("account_name", "")
        
        # Get card details
        last_card_digits = "N/A"
        auto_pay_status = "No"
        if order.customer_profile_id:
            authorize_int = account.integrations.get("authorize.net", {})
            if authorize_int.get("in_use"):
                customer_profile_response = get_customer_profile(
                    str(order.customer_profile_id),
                    authorize_int["api_login_id"],
                    authorize_int["transaction_key"],
                    url=authorize_int["url"],
                )
                credit_card = (
                    customer_profile_response['profile']['paymentProfiles'][0]['payment']
                    .get('creditCard', {})
                    .get('cardNumber', 'XXXX')
                )
                last_card_digits = credit_card[-4:]
                auto_pay_status = "Yes"

        # Determine order status
        status = "Current" if (
            order.status != 'Delinquent'
            and len(order.rent_periods) > 0
            and order.rent_periods[0].calculated_rent_period_balance == 0
        ) else "Overdue"

        # Get transaction list
        past_period_ids = [
            period.id
            for period in sorted(order.rent_periods, key=lambda x: x.start_date)
            if self.is_date_in_past(period.start_date)
        ]

        transactions_list = self.build_transaction_list(order, past_period_ids)

        return {
            'order': order,
            'account': account,
            'customer_info': customer_info,
            'company_name': company_name,
            'last_card_digits': last_card_digits,
            'auto_pay_status': auto_pay_status,
            'status': status,
            'transactions_list': transactions_list
        }

    def _process_transactions_list(self, transactions_data) -> List[RentHistory]:
        """Process transactions data into a sorted list of RentHistory objects.
        
        Args:
            transactions_data: Raw transaction data from base_data['transactions_list']
            
        Returns:
            List[RentHistory]: Sorted list of processed transactions
        """
        transactions_list = []
        
        for trans in transactions_data:
            # Add rent transaction
            transactions_list.append(
                RentHistory(
                    date=trans.date,
                    description=f"RENT {trans.date} - {trans.end_date}",
                    amount="${:.2f}".format(trans.amount + trans.tax),
                    filterable_date=trans.date,
                )
            )
            
            # Add fee transactions
            for fee_name in trans.concatenated_fees:
                if fee_name == 'LATE':
                    start_date = trans.concatenated_fees[fee_name]['start_date']
                    transactions_list.append(
                        RentHistory(
                            date=f"{trans.concatenated_fees[fee_name]['start_date']} thru {trans.concatenated_fees[fee_name]['end_date']}",
                            description=trans.concatenated_fees[fee_name]['description'],
                            amount="${:.2f}".format(
                                trans.concatenated_fees[fee_name]['amount'] + trans.concatenated_fees[fee_name]['tax']
                            ),
                            filterable_date=self.parse_date(start_date).strftime("%m/%d/%y")
                        )
                    )
            
            for fee in trans.fees:
                if fee.name != 'LATE':
                    try:
                        fee_date = (
                            self.parse_date(fee.start_date).strftime("%m/%d/%y")
                            if fee.name in ["DROP_OFF", "PICK_UP"]
                            else self.parse_date(fee.created_at).strftime("%m/%d/%y")
                        )
                    except:
                        fee_date = None
                    transactions_list.append(
                        RentHistory(
                            date=fee_date,
                            description=fee.description,
                            amount="${:.2f}".format(fee.amount + fee.tax),
                            filterable_date=fee_date,
                        )
                    )
            
            # Add other transactions
            for transaction in trans.transaction_type_rent_period.values():
                if transaction:
                    try:
                        formatted_amount = "${:.2f}".format(transaction['amount'])
                        transactions_list.append(
                            RentHistory(
                                date=transaction['date'],
                                description=transaction['description'],
                                amount=f"( {formatted_amount} )",
                                filterable_date=transaction['date'],
                            )
                        )
                    except (KeyError, Exception) as e:
                        logger.info(f"Error processing transaction: {e}")

        # Sort transactions by date
        try:
            return sorted(transactions_list, key=lambda x: datetime.strptime(x.filterable_date, '%m/%d/%y') if x.filterable_date else datetime.now())
        except:
            return transactions_list
        
    async def print_rental_statement_multiple_orders(self, single_customer_id, account_id, requestDates):
        single_customer = await single_customer_crud.get_one(account_id, single_customer_id)

        total_balance_due = Decimal(0)
        orders_details_list = []
        global_status = ""
        for single_customer_order in single_customer.order:
            base_data = await self._get_base_rental_data(single_customer_order.id, account_id)
            if not base_data:
                continue
            order = base_data['order']
            account = base_data['account']
            
            logos = account.cms_attributes.get("logo_settings", {})
            logo = "https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", "")


            transactions_list = self._process_transactions_list(base_data['transactions_list'])
            if(requestDates is not None and len(requestDates.dates) == 2):
                transactions_list = list(filter(
                    lambda obj: (requestDates.dates[0] <= self.parse_date(obj.filterable_date).replace(tzinfo=pytz.UTC) <= requestDates.dates[1] ) if obj.filterable_date and obj.filterable_date != 'None' else False,
                    transactions_list
                ))
            if not transactions_list:
                continue

            # Get container info
            container_info_list = [
                ContainerInfo(
                    title=line_item.abrev_title,
                    container_number=line_item.inventory.container_number if line_item.inventory else "No container attached",
                    location=line_item.inventory_address[0].full_address_computed
                    if line_item.inventory_address
                    else (order.address.full_address if order.address else ""),
                    date_out=line_item.rental_history[-1].rent_ended_at.strftime("%m/%d/%y") if line_item.rental_history else ""
                )
                for line_item in order.line_items
            ]

            
            # Create rent info
            rent_info = RentInfo(
                amount_due="${:.2f}".format(order.calculated_rent_balance),
                start_date=order.calculated_delivered_at.strftime("%m/%d/%y")
                if order.calculated_delivered_at
                else "Not started renting",
                paid_thru=order.calculated_paid_thru,
                date_out="",
            )

            orders_details_list.append({
                "auto_pay_message": "Yes" if order.customer_profile_id else f"Not enrolled in autopay, please call {account.cms_attributes.get('quote_contact_phone', '')}",
                "transactions_list": transactions_list,
                "container_info_list": container_info_list,
                "rent_info": rent_info,
                "order_id": order.display_order_id,
                "paid_thru": order.calculated_paid_thru,
                "balance": "${:.2f}".format(order.calculated_rent_balance),
                "start_date": order.calculated_delivered_at.strftime("%m/%d/%y") if order.calculated_delivered_at else "Not started renting.",
                "po_number": order.purchase_order_number,
                "status": base_data['status'],
                "job_id": order.purchased_order_job_id
            })

            total_balance_due += Decimal(order.calculated_rent_balance)

            if global_status == '':
                global_status = base_data['status']
            elif global_status != 'Overdue' and base_data['status'] == 'Overdue':
                global_status = base_data['status']
        
        # Return complete rental statement
        return RentalStatementMultipleOrders(
            logo=logo,
            title="Rental Statement",
            account_name=account.cms_attributes.get("account_name", ""),
            account_street=account.cms_attributes.get('company_mailing_address', ''),
            account_city_state_zip=account.cms_attributes.get('company_mailing_address', ''),
            account_main_phone=account.cms_attributes.get('quote_contact_phone', ''),
            orders_details_list=orders_details_list,
            customer_name= single_customer.calculated_full_name,
            bill_address= single_customer.customer_contacts[0].customer_address.full_address if  single_customer.customer_contacts 
                and len(single_customer.customer_contacts) > 0 else "",
            current_balance=total_balance_due,
            global_status = global_status
        )

    async def generate_rental_statement_pdf(self, order_id: str, account_id: int) -> RentalStatement:
        base_data = await self._get_base_rental_data(order_id, account_id)
        if not base_data:
            return RentalStatement()

        order = base_data['order']
        account = base_data['account']
        customer_info = base_data['customer_info']
        
        # Set up bill_to information
        bill_to = {
            "customer_name": customer_info.get("calculated_name", ""),
            "bill_address": order.address.full_address,
            "bill_city_state_zip": f"{order.address.city}, {order.address.state} {order.address.zip}",
        }

        # Process transactions for PDF format
        transactions_list = self._process_transactions_list(base_data['transactions_list'])

        # Get container info
        container_info_list = [
            ContainerInfo(
                title=line_item.abrev_title,
                container_number=line_item.inventory.container_number if line_item.inventory else "No container attached",
                location=line_item.inventory_address[0].full_address_computed
                if line_item.inventory_address
                else order.address.full_address
            )
            for line_item in order.line_items
        ]

        # Get logo
        logos = account.cms_attributes.get("logo_settings", {})
        logo = "https://fluffy-jelly-0cb624.netlify.app" + logos.get("logo_path", "")

        # Create rent info
        rent_info = RentInfo(
            amount_due="${:.2f}".format(order.calculated_rent_balance),
            start_date=order.calculated_delivered_at.strftime("%m/%d/%y")
            if order.calculated_delivered_at
            else "Not started renting",
            paid_thru=order.calculated_paid_thru,
            date_out="",
        )

        # Return complete rental statement
        return RentalStatement(
            logo=logo,
            title="Rental Statement",
            account_name=base_data['company_name'],
            customer_orders=str(order.display_order_id),
            account_street=account.cms_attributes.get('company_mailing_address', ''),
            account_city_state_zip=account.cms_attributes.get('company_mailing_address', ''),
            po_num=order.purchase_order_number,
            account_main_phone=account.cms_attributes.get('quote_contact_phone', ''),
            po_job_id=order.purchased_order_job_id,
            current_balance="${:.2f}".format(order.calculated_rent_balance),
            auto_pay_message="Yes" if order.customer_profile_id else f"Not enrolled in autopay, please call {account.cms_attributes.get('quote_contact_phone', '')}",
            status=base_data['status'],
            customer_name=bill_to['customer_name'],
            bill_address=bill_to['bill_address'],
            bill_city_state_zip="",
            container_info=container_info_list,
            rent_info=rent_info,
            rent_history=transactions_list,
            notes=str(order.note),
            last_card_digits=base_data['last_card_digits'],
        )

    async def generate_rental_statement_web(self, order_id: str, account_id: int, data: RentalStatementDataRequest = None) -> dict:
        base_data = await self._get_base_rental_data(order_id, account_id)
        if not base_data:
            return {}

        order = base_data['order']
        customer_info = base_data['customer_info']

        # Create customer detail
        customer_detail = CustomerDetail(
            name=customer_info.get("calculated_name", ""),
            email=customer_info.get("email", ""),
            address=order.address.full_address,
            delivery_address=order.calculated_container_delivery_addresses
        )

        # Create order detail
        order_detail = OrderDetail(
            last_card_digits=base_data['last_card_digits'],
            container_type=order.calculated_abreviated_line_items_title,
            auto_pay=base_data['auto_pay_status'],
            status=order.status,
            display_order_id=order.display_order_id,
            start_date=order.calculated_delivered_at.strftime("%m/%d/%y")
            if order.calculated_delivered_at
            else "Not started renting",
            late_fee_date="",
            amount_due=str(order.calculated_rent_balance)
        )

        # Create order info
        order_info = {
            'paid_thru': order.calculated_paid_thru,
            'first_rent': (
                order.calculated_delivered_at.strftime("%m/%d/%y")
                if order.calculated_delivered_at and base_data['transactions_list']
                else "Not started renting"
            )
        }

        # Process transactions for PDF format
        transactions_list = self._process_transactions_list(base_data['transactions_list'])
        if(data is not None and data.partial and len(data.partialRentalStatementDates) == 2):
            transactions_list = list(filter(
                lambda obj: data.partialRentalStatementDates[0] <= self.parse_date(obj.filterable_date).replace(tzinfo=pytz.UTC) <= data.partialRentalStatementDates[1],
                transactions_list
            ))

        return {
            'transactions_list': transactions_list,
            'customer_detail': customer_detail,
            'order_detail': order_detail,
            'company_name': base_data['company_name'],
            'order_info': order_info,
        }

    def is_date_in_past(self, target_date):
        current_date = datetime.now() - timedelta(days=1)
        if not target_date:
            return None
        return target_date.replace(tzinfo=None) <= current_date.replace(tzinfo=None)

    def find_last_transaction_paid(self, period_list):
        for i, period in enumerate(period_list):
            if period.calculated_rent_period_total_balance != 0:
                if i > 0:
                    return period_list[i - 1]
                else:
                    return None


customer_statement_controller = CustomerStatement()
