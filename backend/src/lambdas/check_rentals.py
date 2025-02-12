# Python imports
import asyncio
import calendar
import uuid

# import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union
import traceback
import sys
# Pip imports
import pytz
from loguru import logger
from tortoise import Tortoise
from tortoise.transactions import atomic

# Internal imports
from src.database.tortoise_init import init_models
from src.schemas.rent_period_fee import RentPeriodFeeIn


# enable schemas to read relationship between models
# flakes8: noqa
init_models()

# Internal imports
from src.config import settings  # noqa: E402
from src.controllers import fee_type as fee_type_controller  # noqa: E402
from src.controllers import rent_period as rent_period_controller  # noqa: E402
from src.controllers import rent_period_fee as rent_period_fee_controller  # noqa: E402
from src.controllers import transaction_type as transaction_type_controller  # noqa: E402
from src.controllers.customer_statement import customer_statement_controller  # noqa: E402
from src.controllers.orders import generate_rental_invoice_pdf_docugenerate
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.fee_crud import fee_crud  # noqa: E402
from src.crud.fee_type_crud import fee_type_crud
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.rent_period_crud import RentPeriodIn, rent_period_crud
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account  # noqa: E402
from src.database.models.fee_type import FeeType  # noqa: E402
from src.database.models.orders.order import Order  # noqa: E402
from src.database.models.rent_period import RentPeriod  # noqa: E402
from src.schemas.fee import FeeIn  # noqa: E402
from src.schemas.orders import OrderInUpdate, OrderOut  # noqa: E402
from src.schemas.payment import Payment  # noqa: E402
from src.schemas.transaction_type import TransactionTypesIn  # noqa: E402
from src.services.notifications import email_service_mailersend  # noqa: E402
from src.services.notifications.email_service_mailersend import (  # noqa: E402
    ChargedRental,
    Data,
    SendChargedRental,
    send_charged_rentals,
    send_check_rentals_admin_email,
)
from src.services.payment.authorize_pay_service import (  # noqa: E402
    charge_customer_profile,
    get_customer_profile,
    get_customer_profile_transactions,
)
from src.crud.partial_order_crud import partial_order_crud


AMOBILEBOX_PAST_DUE_STATUS = "Delinquent"
AMOBILEBOX_CURRENT_STATUS = "Delivered"
AMOBILEBOX_TEST_ORDER_ID = "b3df30b1-bd09-4a19-aca8-0a81f3f279a0"
# sys.path.append("..")
# init Tortoise before pydantic imports


class HandleLateRentalLogicObj:
    def __init__(
        self,
        order_status: str = "",
        charge_customer_profile_response: Union[dict, None] = None,
        paid_down_rent_periods: Union[List[RentPeriod], None] = None,
        amount_charged: str = "",
        display_order_id: str = "",
        is_approved: bool = False,
    ):
        self.order_status = order_status
        self.charge_customer_profile_response = charge_customer_profile_response
        self.paid_down_rent_periods = paid_down_rent_periods
        self.amount_charged = amount_charged
        self.display_order_id = display_order_id
        self.is_approved = is_approved


def handler(event, context):
    is_charge = event.get("CHARGE", False)
    if is_charge == "true" or is_charge == "TRUE":
        is_charge = True
    if is_charge == "false" or is_charge == "FALSE":
        is_charge = False

    is_email = event.get("EMAIL", False)
    if is_email == "true" or is_email == "TRUE":
        is_email = True
    if is_email == "false" or is_email == "FALSE":
        is_email = False

    result = asyncio.run(async_handler(event, context, is_charge))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context, is_charge):
    await Tortoise.init(config=TORTOISE_ORM)
    accounts: List[Account] = await account_crud.get_all()
    admin_table = {}
    for account in accounts:
        authorize_int_rentals = account.integrations.get("authorize", {}).get("rentals", {})

        is_send_email_notifications: bool = account.cms_attributes.get("rent_options", {}).get(
            "is_send_email_notifications"
        )
        is_process_charges: bool = account.cms_attributes.get("rent_options", {}).get("is_process_charges")

        admin_table[account.id] = {}

        if authorize_int_rentals.get("in_use"):
            await handle_authorize_accounts(
                account,
                authorize_int_rentals['api_login_id'],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
                is_process_charges=is_process_charges,
                is_send_email_notifications=is_send_email_notifications,
                is_charge=is_charge,
                admin_table=admin_table,
            )

        # if usa_epay_int.get("in_use"):
        #     await handle_usa_epay_accounts(account, usa_epay_int['api_key'])
    account: Account = await account_crud.get_one(1)
    logger.info("Sending rental admin emal " + str(admin_table))
    send_check_rentals_admin_email(admin_table, account, accounts)


async def verify_charge_day(
    order: Order,
    latest_transaction_created: Union[datetime, None],
    latest_transaction_approved: bool,
    current_date: datetime,
    one_day_rent_periods: bool,
    overdue_rent_periods: list,
):
    if not one_day_rent_periods:
        charge_day = order.rent_due_on_day

        if not charge_day:
            logger.error(f"Charge day is null for order {order.display_order_id}")
            return False

        # Check if the charge day is valid for the current month
        if charge_day > 28 and current_date.month == 2:
            # For February, set the charge day to the last day (28 or 29)
            last_day_of_month = 29 if calendar.isleap(current_date.year) else 28
            charge_day = last_day_of_month

        elif charge_day > 30 and current_date.month in [4, 6, 9, 11]:
            # For months with 30 days, set the charge day to the last day (30)
            charge_day = 30

        # Check if the charge day has already passed in the current month
        if current_date.day > charge_day:
            # If yes, set the next charge date to the same day in the next month
            month = (current_date.month + 1) % 12 if current_date.month + 1 > 12 else current_date.month + 1
            if current_date.month + 1 > 12:
                year = current_date.year + 1
            else:
                year = current_date.year
            next_charge_date = current_date.replace(year=year, month=month, day=charge_day)
        else:
            # If not, set the next charge date to the same day in the current month
            next_charge_date = current_date.replace(day=charge_day)

        if len(overdue_rent_periods) > 0:
            next_charge_date = current_date
    else:
        next_charge_date = current_date
        for rent_period in order.rent_periods:
            if current_date > rent_period.start_date.date() and current_date <= rent_period.end_date.date():
                next_charge_date = rent_period.end_date.date()

    # Print the next charge date
    logger.info(f"Order {order.display_order_id}, Next charge date: {next_charge_date.strftime('%Y-%m-%d %H:%M:%S')}")

    for rent_period in order.rent_periods:
        if current_date == rent_period.start_date - timedelta(days=7):
            logger.info(f'Order {order.display_order_id}, Next charge date is 7 days away.')
            account = await account_crud.get_one(order.account_id)
            if order.send_pdf_invoice:
                pdf_url = await generate_rental_invoice_pdf_docugenerate(
                    None, str(order.id), rent_period.start_date + timedelta(days=1)
                )

                await rent_period_crud.update(
                    rent_period.id, RentPeriodIn(amount_owed=rent_period.amount_owed, pdf_url=pdf_url)
                )
                body = "Download invoice from " + pdf_url
                email_service_mailersend.send_incoming_rental_payment_invoice(
                    order.display_order_id, body, "developers@mobilestoragetech.com", account
                )
            else:
                BASE_URL = f"{account.cms_attributes.get('sales_link_base_url')}/#"
                url = BASE_URL + "/rental_invoice/" + str(order.id)

                body = "Open invoice at " + url
                email_service_mailersend.send_incoming_rental_payment_invoice(
                    order.display_order_id, body, "developers@mobilestoragetech.com", account
                )

            break

    # if next_charge_date is seven days away
    if next_charge_date == current_date + timedelta(days=7):
        logger.info(f'Order {order.display_order_id}, Next charge date is 7 days away.')
        pass

    if (
        latest_transaction_created
        and next_charge_date == latest_transaction_created.date()
        and latest_transaction_approved
    ):
        logger.info(f'Order {order.display_order_id}, They have paid today.')
        return False

    # Check if the transaction date is the same day in the month as today
    return next_charge_date == current_date


def is_charge_customer_profile_resp_approved(resp: dict) -> bool:
    approved: bool
    if "errorMessage" in resp:
        approved = False
    else:
        approved = (
            resp.get('transactionResponse', {}).get('messages')[0].get('description')
            == 'This transaction has been approved.'
        )
    return approved


async def handle_late_rental_logic(
    today: datetime,
    order: Order,
    grace_period: int,
    account: Account,
    is_autopay: bool = False,
    customer_payment_profile_id: str = "",
    api_key: str = "",
    trans_key: str = "",
    url: str = "",
    is_process_charges: bool = False,
    is_charge: bool = False,
    is_send_email_notifications: bool = False,
    admin_table={},
) -> HandleLateRentalLogicObj:

    periods: List[RentPeriod]
    # period is late rent period
    first_period: RentPeriod
    order_status: str = ""
    charge_customer_profile_resp: Union[dict, None] = None

    # we point it to the rent period balance bc that determines if they are current or not
    # We want to grab all the periods who have rent period balances > 0 and that are current or in the past
    periods = [
        rp
        for rp in order.rent_periods
        if rp.calculated_rent_period_balance > 0
        and (rp.end_date is not None and (rp.start_date.date() <= today and today <= rp.end_date.date()))
    ]

    periods.sort(key=lambda x: x.start_date)

    is_periods_populated: bool = len(periods) > 0
    current_period = periods[0] if is_periods_populated else None
    # fetch current rent period as that is the period the fee will be applied to and not the first period
    for period in periods:
        if current_period.end_date.date() >= today >= current_period.start_date.date():
            current_period = period
            break
    total_amt: Decimal = 0
    is_approved: Union[bool, None] = None

    if not is_charge and is_periods_populated and today > current_period.start_date.date():
        order_status = AMOBILEBOX_PAST_DUE_STATUS

        # if it is autopay and we have processed the charges
        if is_autopay and is_process_charges and is_send_email_notifications:
            rental_statement_email_message = f"Your card didn't work, late fee applied for {order.display_order_id}."
            order_dict: dict = order.__dict__
            order_dict["customer"] = order_dict['customer'].__dict__
            order_dict["account_name"] = account.name
            response = await email_service_mailersend.send_transaction_failed(order_dict)
            if response:
                admin_table[account.id][order.display_order_id]['customer_emailed'] = True

        # if it is autopay and we have not processed the charges
        elif is_autopay and not is_process_charges and is_send_email_notifications:
            rental_statement_email_message = f"Late fees have been applied for {order.display_order_id}."
            order_dict: dict = order.__dict__
            order_dict["customer"] = order_dict['customer'].__dict__
            order_dict["account_name"] = account.name
            response = await email_service_mailersend.send_late_fee_email(order_dict)
            if response:
                admin_table[account.id][order.display_order_id]['customer_emailed'] = True

        if is_send_email_notifications:
            statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
            response = email_service_mailersend.send_customer_rental_statement(
                statement['transactions_list'],
                statement['customer_detail'],
                statement['order_detail'],
                statement['company_name'],
                statement['order_info'],
                rental_statement_email_message,
            )
            if response:
                admin_table[account.id][order.display_order_id]['customer_emailed'] = True
    elif is_charge and order.is_late_fee_applied and is_periods_populated and today > current_period.start_date.date():
        order_status = AMOBILEBOX_PAST_DUE_STATUS
        total_late_fees_amt: Decimal = 0
        interval: timedelta = today - current_period.start_date.date()

        try:
            if interval.days == grace_period:
                late_fee_type = await fee_type_crud.get_by_name(account.id, 'LATE')
                late_fee_per_line_item = late_fee_type.line_item_level
                if late_fee_per_line_item:
                    for i in range(len(order.line_items)):
                        total_late_fees_amt = grace_period * handle_late_fee_calc(interval, account, grace_period)
                        total_amt += total_late_fees_amt
                else:
                    total_late_fees_amt = grace_period * handle_late_fee_calc(interval, account, grace_period)
                    total_amt += total_late_fees_amt
                await handle_late_fee_creation(
                    total_late_fees_amt * len(order.line_items) if late_fee_per_line_item else total_late_fees_amt,
                    current_period,
                    account.id,
                )

            if interval.days > grace_period:
                late_fee_type = await fee_type_crud.get_by_name(account.id, 'LATE')
                late_fee_per_line_item = late_fee_type.line_item_level
                if late_fee_per_line_item:
                    for i in range(len(order.line_items)):
                        total_late_fees_amt = handle_late_fee_calc(interval, account, grace_period)
                        total_amt += total_late_fees_amt
                else:
                    total_late_fees_amt = handle_late_fee_calc(interval, account, grace_period)
                    total_amt += total_late_fees_amt
                await handle_late_fee_creation(
                    total_late_fees_amt * len(order.line_items) if late_fee_per_line_item else total_late_fees_amt,
                    current_period,
                    account.id,
                )
        except Exception as e:
            await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))


        for period in periods:
            total_amt += period.calculated_rent_period_total_balance

        if is_autopay and is_process_charges:
            order_details = {"display_order_id": order.display_order_id, "amount": total_amt}

            try:
                # only if we have set the process charges env var in the lambda will this run
                charge_customer_profile_resp = charge_customer_profile(
                    order_details,
                    order.customer_profile_id,
                    customer_payment_profile_id,
                    api_key,
                    trans_key,
                    url,
                )

                is_approved = is_charge_customer_profile_resp_approved(charge_customer_profile_resp)
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

            if is_approved:
                admin_table[account.id][order.display_order_id]['customer_paid'] = "Successfull"
            else:
                admin_table[account.id][order.display_order_id]['customer_paid'] = "Unsuccessfull"
            if is_approved:
                order_status = AMOBILEBOX_CURRENT_STATUS

            logger.info(charge_customer_profile_resp)
        else:
            charge_customer_profile_resp = None
    elif is_charge:
        order_status = AMOBILEBOX_CURRENT_STATUS

    # if this is not an autopay scenario, then we want the return obj to just have the orderstatus populated
    response_obj: HandleLateRentalLogicObj = HandleLateRentalLogicObj(
        order_status=order_status,
        charge_customer_profile_response=charge_customer_profile_resp,
        paid_down_rent_periods=periods if is_autopay else None,
        amount_charged=str(total_amt),
        display_order_id=order.display_order_id,
        is_approved=is_approved,
    )

    return response_obj


async def handle_update_order_status(updated_status: str, existing_order: Order):

    order_dict = {
        "status": updated_status,
        "user_id": existing_order.user.id,
        "account_id": existing_order.account_id,
    }

    updated_order = await order_crud.update(
        existing_order.account_id,
        existing_order.id,
        OrderInUpdate(**order_dict),
    )

    return updated_order


def handle_late_fee_calc(interval: timedelta, account: Account, grace_period: int) -> Decimal:
    late_fee = account.cms_attributes.get("rent_options", {}).get("late_fee", 1)
    # total_late_fees_amt: Decimal = 0

    # if interval.days >= grace_period:
    #     total_late_fees_amt = interval.days * late_fee

    return late_fee


async def handle_late_fee_creation(total_late_fees_amt: Decimal, rent_period: RentPeriod, account_id: int):

    late_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(
        account_id=account_id, fee_type_name="LATE"
    )

    create_fee: RentPeriodFeeIn = RentPeriodFeeIn(
        fee_amount=total_late_fees_amt, type_id=late_fee_type.id, rent_period_id=rent_period.id
    )
    await rent_period_fee_controller.create_rent_period_fees([create_fee])


# deprecated. Only used for usaepay
async def handle_late_fee(order: OrderOut, account: Account, next_charge_date: datetime, latest_transaction: dict):
    logger.info('Last transaction failed')

    # Get grace period and late fee from account configuration
    grace_period = account.cms_attributes.get("rent_options", {}).get("grace_period", 5)
    late_fee = account.cms_attributes.get("rent_options", {}).get("late_fee", 1)

    last_charge_date: datetime = next_charge_date.replace(month=next_charge_date.month - 1, day=next_charge_date.day)

    # Calculate the deadline for the latest transaction to be within the grace period
    deadline_for_late_fee = last_charge_date + timedelta(days=grace_period)

    # Check if the latest transaction is 5 days after the initial transaction
    if latest_transaction['created_at'] == deadline_for_late_fee:
        logger.info('Late fee should be charged.')
        total_fees = late_fee * grace_period
        create_fee: FeeIn = FeeIn(fee_amount=total_fees, fee_type=FeeType.LATE, order_id=order['id'])
        await fee_crud.create(create_fee)
    elif latest_transaction["created_at"] > deadline_for_late_fee:
        logger.info('Additional late fee should be charged.')
        total_fees = late_fee
        create_fee: FeeIn = FeeIn(fee_amount=total_fees, fee_type=FeeType.LATE, order_id=order['id'])
        await fee_crud.create(create_fee)
    else:
        logger.info('Late fee not applicable.')
        # No late fee is charged

    return False


async def handle_auto_pay_orders(
    order,
    account,
    api_key,
    trans_key,
    url,
    is_process_charges,
    current_date,
    grace_period,
    one_day_rent_periods,
    charged_rentals,
    rent_options,
    is_charge,
    is_send_email_notifications,
    admin_table,
):
    order_status: str = ""
    handle_late_rental_logic_obj: HandleLateRentalLogicObj = HandleLateRentalLogicObj()
    charge_customer_profile_resp: Union[dict, None] = None
    try:
        customer_profile = get_customer_profile(order.customer_profile_id, api_key, trans_key, url)
    except Exception as e:
        await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))
    credit_card_payment_profile_id = None
    bank_account_payment_profile_id = None

    if customer_profile.get('errorMessage'):
        logger.error(f"Error getting customer profile for order {order.display_order_id}")
        return

    payment_profiles = customer_profile.get('profile', {}).get('paymentProfiles', [{}])

    for payment_profile in payment_profiles:
        if payment_profile.get('payment', {}).get('creditCard', {}):
            credit_card_payment_profile_id = payment_profile.get('customerPaymentProfileId')
        if payment_profile.get('payment', {}).get('bankAccount', {}):
            bank_account_payment_profile_id = payment_profile.get('customerPaymentProfileId')

    if not credit_card_payment_profile_id and not bank_account_payment_profile_id:
        logger.error(
            f"Error getting payment profile for order {order.display_order_id} for both credit card and bank account"
        )
        return

    try:
        final_payment_profile_id = None
        if credit_card_payment_profile_id and bank_account_payment_profile_id:
            if not order.primary_payment_method:
                transactionsResponse = get_customer_profile_transactions(
                    order.customer_profile_id, credit_card_payment_profile_id, api_key, trans_key, url
                )
                final_payment_profile_id = credit_card_payment_profile_id
            elif order.primary_payment_method == 'CREDIT_CARD':
                transactionsResponse = get_customer_profile_transactions(
                    order.customer_profile_id, credit_card_payment_profile_id, api_key, trans_key, url
                )
                final_payment_profile_id = credit_card_payment_profile_id
            else:
                transactionsResponse = get_customer_profile_transactions(
                    order.customer_profile_id, bank_account_payment_profile_id, api_key, trans_key, url
                )
                final_payment_profile_id = bank_account_payment_profile_id
    

        if not final_payment_profile_id and credit_card_payment_profile_id:
            transactionsResponse = get_customer_profile_transactions(
                order.customer_profile_id, credit_card_payment_profile_id, api_key, trans_key, url
            )
            final_payment_profile_id = credit_card_payment_profile_id
        elif not final_payment_profile_id and bank_account_payment_profile_id:
            transactionsResponse = get_customer_profile_transactions(
                order.customer_profile_id, bank_account_payment_profile_id, api_key, trans_key, url
            )
            final_payment_profile_id = bank_account_payment_profile_id
    except Exception as e:
        await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

    latest_transaction_approved: bool = True
    latest_transaction: Union[str, None] = None

    # if they are just starting autopay, they will not have any transactions, so if
    # this is teh first time they have been on autopay, then we will just force it to be
    # latest_transaction_approved = true and failed = false. This way the logic can run
    # but if they have had past transactions, then it will check them appropriately
    if transactionsResponse['totalNumInResultSet'] != 0:
        transactions_list: list = transactionsResponse['transactions']
        transactions_list.sort(key=lambda x: x['submitTimeUTC'], reverse=True)
        latest_transaction = transactions_list[0]

        latest_transaction_approved = latest_transaction['transactionStatus'] in [
            'settledSuccessfully',
            'capturedPendingSettlement',
        ]

    latest_transaction_created: Union[datetime, None] = (
        datetime.strptime(latest_transaction['submitTimeUTC'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if latest_transaction
        else latest_transaction
    )

    current_and_overdue_rent_periods = [
        rp
        for rp in order.rent_periods
        if rp.start_date and rp.start_date.date() <= current_date
        if rp.calculated_rent_period_total_balance > 0
    ]

    try:
        # today is crt_rent_period.start_date
        is_charge_day: bool = await verify_charge_day(
            order,
            latest_transaction_created,
            latest_transaction_approved,
            current_date,
            one_day_rent_periods,
            current_and_overdue_rent_periods,
        )
    except Exception as e:
        await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))


    if not latest_transaction_approved:
        # we point it to the rent period balance bc that determines if they are current or not
        # we are either going to charge them the entirety of their total balance + just accrued late fees
        handle_late_rental_logic_obj = await handle_late_rental_logic(
            today=current_date,
            order=order,
            grace_period=grace_period,
            account=account,
            is_autopay=order.is_autopay,
            customer_payment_profile_id=final_payment_profile_id,
            api_key=api_key,
            trans_key=trans_key,
            url=url,
            is_process_charges=is_process_charges,
            is_charge=is_charge,
            is_send_email_notifications=is_send_email_notifications,
            admin_table=admin_table,
        )
        if not is_charge:
            return
        order_status = handle_late_rental_logic_obj.order_status
        charge_customer_profile_resp = handle_late_rental_logic_obj.charge_customer_profile_response

        # if it doesnt find any outstanding periods, then it will return "" for order_status
        if order_status == "":
            logger.info(f"Order {order.display_order_id} is current. Exiting.")
            return
        # but if charge_customer_profile_resp is not none, that means they were charged, or it atleast
        # attempted to charge them so we need to prep the email
        if charge_customer_profile_resp is not None:
            charged_rental: ChargedRental = ChargedRental(
                date=datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S'),
                amount=handle_late_rental_logic_obj.amount_charged,
                display_order_id=handle_late_rental_logic_obj.display_order_id,
                is_approved=handle_late_rental_logic_obj.is_approved,
            )
            charged_rentals.append(charged_rental)

    elif not is_charge and is_charge_day and latest_transaction_approved:
        if is_send_email_notifications:
            statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
            try:
                response = email_service_mailersend.send_customer_rental_statement(
                    statement['transactions_list'],
                    statement['customer_detail'],
                    statement['order_detail'],
                    statement['company_name'],
                    statement['order_info'],
                    f"You have been successfully charged the monthly rent for order {order.display_order_id} today.",
                    account,
                )
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

            if response:
                admin_table[account.id][order.display_order_id]['customer_emailed'] = True
        return

    # we point it to the rent period balance bc that determines if they are current or not
    elif is_charge and is_charge_day and order.calculated_remaining_order_balance > 0:
        # or just what they owe on their charge day

        balance = sum(
            [x.calculated_rent_period_total_balance for x in order.rent_periods if x.start_date.date() <= current_date]
        )

        order_details = {
            "display_order_id": order.display_order_id,
            "amount": balance,
        }
        if is_process_charges:
            try:
                charge_customer_profile_resp = charge_customer_profile(
                    order_details,
                    order.customer_profile_id,
                    final_payment_profile_id,
                    api_key,
                    trans_key,
                    url,
                )
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

            try:
                approved = is_charge_customer_profile_resp_approved(charge_customer_profile_resp)
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

            if approved:
                admin_table[account.id][order.display_order_id]['customer_paid'] = "Successfull"
            else:
                admin_table[account.id][order.display_order_id]['customer_paid'] = "Unsuccessfull"

            charged_rental: ChargedRental = ChargedRental(
                date=datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S'),
                amount=order_details.get("amount", 0),
                display_order_id=order_details.get("display_order_id", ""),
                is_approved=approved,
            )
            charged_rentals.append(charged_rental)
        else:
            charge_customer_profile_resp = None

    if not is_charge:
        return

    if charge_customer_profile_resp:
        try:
            approved = is_charge_customer_profile_resp_approved(charge_customer_profile_resp)
        except Exception as e:
            await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

        if approved:
            paid_w_method = "Credit Card" if credit_card_payment_profile_id else "Bank Account ACH"
            notes: str = f"This period was paid by autopay with the transaction id: {charge_customer_profile_resp.get('transactionResponse', '').get('transId', '')} and paid using {paid_w_method}"
            group_id = uuid.uuid4()
            payment_profiles = customer_profile.get('profile', {}).get('paymentProfiles', [{}])

            for payment_profile in payment_profiles:
                bill_to = payment_profile.get('billTo', {})
                payment_credit_card = payment_profile.get('payment', {}).get('creditCard', {})
                payment_ach = payment_profile.get('payment', {}).get('bankAccount', {})

            if payment_ach:
                payment_request = Payment(
                    first_name=bill_to.get('firstName', ''),
                    last_name=bill_to.get('lastName', ''),
                    zip=bill_to.get('zip', ''),
                    avs_street=bill_to.get('address', ''),
                    city=bill_to.get('city', ''),
                    state=bill_to.get('state', ''),
                    accountNumber=payment_ach.get('accountNumber', ''),
                    routingNumber=payment_ach.get('routingNumber', ''),
                    total_paid=0,
                    order_id=str(order.id),
                    display_order_id=order.display_order_id,
                    convenience_fee_total=0,
                    merchant_name="",
                    type="ACH",
                    rent_period_ids=[str(rp.id) for rp in current_and_overdue_rent_periods]
                    if not handle_late_rental_logic_obj.paid_down_rent_periods
                    else [str(period.id) for period in handle_late_rental_logic_obj.paid_down_rent_periods],
                )
            else:
                payment_request = Payment(
                    first_name=bill_to.get('firstName', ''),
                    last_name=bill_to.get('lastName', ''),
                    zip=bill_to.get('zip', ''),
                    avs_street=bill_to.get('address', ''),
                    city=bill_to.get('city', ''),
                    state=bill_to.get('state', ''),
                    cardNumber=payment_credit_card.get('cardNumber', ''),
                    expirationDate=payment_credit_card.get('expirationDate', ''),
                    cardCode=payment_credit_card.get('cardCode', 111),
                    total_paid=0,
                    order_id=str(order.id),
                    display_order_id=order.display_order_id,
                    convenience_fee_total=0,
                    merchant_name="",
                    type="CREDIT",
                    rent_period_ids=[str(rp.id) for rp in current_and_overdue_rent_periods]
                    if not handle_late_rental_logic_obj.paid_down_rent_periods
                    else [str(period.id) for period in handle_late_rental_logic_obj.paid_down_rent_periods],
                )

            try:
                await rent_period_controller.handle_rent_period_credit_card_pay(
                    payment_request, order, rent_options, False, notes=notes, group_id=group_id
                )
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))


            order_status = AMOBILEBOX_CURRENT_STATUS if order_status == '' else order_status
            return order_status


@atomic()
async def handle_authorize_accounts(
    account: Account,
    api_key: str,
    trans_key: str,
    url: str,
    is_process_charges: bool = False,
    is_send_email_notifications: bool = False,
    is_charge: bool = True,
    admin_table={},
):
    orders: List[Order] = await partial_order_crud.search_orders(
        account.id,
        status="Delivered,Delinquent,first_payment_received",
        order_types="RENT,RENT_TO_OWN",
    )
    rent_options: dict = account.cms_attributes.get("rent_options")
    grace_period: int = rent_options.get('grace_period')
    current_date: datetime = datetime.now(pytz.utc).date()
    charged_rentals: List[ChargedRental] = []

    for order in orders:
        admin_table[account.id][order.display_order_id] = {}
        # TODO All this is used for testing comment out after
        # current_date = current_date.replace(
        # year=2025, month=10, day=29
        # )
        # current_date = current_date.replace(year=2025, month=8, day=5)
        # current_date = current_date.replace(
        #     month=current_date.month + 5, day=order.rent_due_on_day + 1
        # )
        # current_date = current_date.replace(month=current_date.month + 2, day=order.rent_due_on_day + grace_period)
        # current_date = current_date.replace(month=current_date.month + 2, day=order.rent_due_on_day + grace_period + 1)


        admin_table[account.id][order.display_order_id]['customer_paid'] = "No Attempt"
        admin_table[account.id][order.display_order_id]['customer_emailed'] = False

        order_status: str = ""
        is_order_status_changed: bool = False

        one_day_rent_periods = False
        if len(order.rent_periods) >= 1:
            if (
                order.rent_periods[0].start_date is not None
                and order.rent_periods[0].end_date is not None
                and abs(order.rent_periods[0].start_date.date() - order.rent_periods[0].end_date.date())
                == timedelta(days=1)
            ):
                one_day_rent_periods = True

        # This signifies that we are in autopay
        if order.is_autopay:
            order_status = await handle_auto_pay_orders(
                order,
                account,
                api_key,
                trans_key,
                url,
                is_process_charges,
                current_date,
                grace_period,
                one_day_rent_periods,
                charged_rentals,
                rent_options,
                is_charge,
                is_send_email_notifications,
                admin_table,
            )
        else:
            current_and_overdue_rent_periods = [
                rp
                for rp in order.rent_periods
                if rp.start_date and rp.start_date.date() <= current_date
                if rp.calculated_rent_period_total_balance > 0
            ]
            # non auto paid user
            try:
                is_charge_day = await verify_charge_day(
                    order, None, None, current_date, one_day_rent_periods, current_and_overdue_rent_periods
                )
            except Exception as e:
                await email_service_mailersend.send_exception_email("check_rentals", str(''.join(traceback.format_exception(*sys.exc_info()))))

            if not is_charge and is_charge_day and is_send_email_notifications:
                statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
                response = email_service_mailersend.send_customer_rental_statement(
                    statement['transactions_list'],
                    statement['customer_detail'],
                    statement['order_detail'],
                    statement['company_name'],
                    statement['order_info'],
                    f"You are expected to pay monthly rent for order {order.display_order_id} today.",
                )
                if response:
                    admin_table[account.id][order.display_order_id]['customer_emailed'] = True

                return

            handle_late_rental_logic_obj = await handle_late_rental_logic(
                today=current_date,
                order=order,
                grace_period=grace_period,
                account=account,
                is_charge=is_charge,
                admin_table=admin_table,
            )
            order_status = handle_late_rental_logic_obj.order_status

            if is_charge_day:
                logger.info(f"Order {order.display_order_id} is due to be charged today, but not on autopay. Skipping.")
                pass

        if order_status:
            is_order_status_changed = (order.status.lower() != order_status.lower()) and order_status != ""
        else:
            is_order_status_changed = False

        if is_order_status_changed:
            await handle_update_order_status(order_status, order)

    send_charged_rentals_data: Data = Data(
        company_name=account.name, charged_rentals=charged_rentals, total_rentals_charged=len(charged_rentals)
    )

    # we only want to send a charge email if there were actually rentals that were charged
    if int(send_charged_rentals_data.total_rentals_charged) > 0 and is_send_email_notifications:
        send_charged_rentals_obj: SendChargedRental = SendChargedRental(
            email=settings.EMAIL_TO, data=send_charged_rentals_data
        )

        response = send_charged_rentals(send_charged_rentals_obj, settings.EMAIL_TO)
        if response:
            admin_table[account.id][order.display_order_id]['customer_emailed'] = True


#handler({"EMAIL": "CHARGE"}, None)
