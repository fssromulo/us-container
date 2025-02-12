# Python imports
import asyncio

# import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union

# Pip imports
import pytz
from loguru import logger
from tortoise import Tortoise
from tortoise.transactions import atomic

# Internal imports
from src.check_rentals import verify_charge_day
from src.database.tortoise_init import init_models


# enable schemas to read relationship between models
# flakes8: noqa
init_models()

# Internal imports
from src.controllers.customer_statement import customer_statement_controller  # noqa: E402
from src.crud.account_crud import account_crud  # noqa: E402

# from src.crud.total_order_balance_crud import total_order_balance_crud
from src.crud.order_crud import order_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account  # noqa: E402
from src.database.models.account import RentPeriod  # noqa: E402
from src.database.models.orders.order import Order  # noqa: E402
from src.services.notifications import email_service_mailersend  # noqa: E402
from src.services.payment.authorize_pay_service import (  # noqa: E402
    get_customer_profile,
    get_customer_profile_transactions,
)


AMOBILEBOX_PAST_DUE_STATUS = "Delinquent"
AMOBILEBOX_CURRENT_STATUS = "Delivered"
AMOBILEBOX_TEST_ORDER_ID = "204b452b-1d1e-4507-952f-f56ac0942e2b"
# sys.path.append("..")
# init Tortoise before pydantic imports


class HandleLateRentalLogicObj:
    def __init__(
        self,
        order_status: str = "",
        charge_customer_profile_response: Union[dict, None] = None,
        paid_down_rent_periods: Union[List[RentPeriod], None] = None,
    ):
        self.order_status = order_status
        self.charge_customer_profile_response = charge_customer_profile_response
        self.paid_down_rent_periods = paid_down_rent_periods


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    accounts: List[Account] = await account_crud.get_all()

    for account in accounts:
        authorize_int_rentals: dict = account.integrations.get("authorize", {}).get('rentals', {})
        is_send_email_notifications: bool = account.cms_attributes.get("rent_options", {}).get(
            "is_send_email_notifications"
        )
        is_process_charges: bool = account.cms_attributes.get("rent_options", {}).get("is_process_charges")

        if authorize_int_rentals.get("in_use"):
            await handle_authorize_accounts(
                account,
                authorize_int_rentals['api_login_id'],
                authorize_int_rentals["transaction_key"],
                url=authorize_int_rentals["url"],
                is_process_charges=is_process_charges,
                is_send_email_notifications=is_send_email_notifications,
            )


async def handle_late_rental_logic(
    today: datetime,
    order: Order,
    grace_period: int,
    account: Account,
    is_autopay: bool = False,
    is_process_charges: bool = False,
    is_send_email_notifications: bool = False,
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
        and (rp.end_date.date() <= today or (rp.start_date.date() <= today and today <= rp.end_date.date()))
    ]

    periods.sort(key=lambda x: x.start_date)

    is_periods_populated: bool = len(periods) > 0
    first_period = periods[0] if is_periods_populated else None

    if is_periods_populated and today > first_period.start_date.date():
        order_status = AMOBILEBOX_PAST_DUE_STATUS

        # if it is autopay and we have processed the charges
        if is_autopay and is_process_charges and is_send_email_notifications:
            rental_statement_email_message = f"Your card didn't work, late fee applied for {order.display_order_id}."
            order_dict: dict = order.__dict__
            order_dict["customer"] = order_dict['customer'].__dict__
            order_dict["account_name"] = account.name
            email_service_mailersend.send_transaction_failed(order_dict)
        # if it is autopay and we have not processed the charges
        elif is_autopay and not is_process_charges and is_send_email_notifications:
            rental_statement_email_message = f"Late fees have been applied for {order.display_order_id}."
            order_dict: dict = order.__dict__
            order_dict["customer"] = order_dict['customer'].__dict__
            order_dict["account_name"] = account.name
            email_service_mailersend.send_late_fee_email(order_dict)

        else:
            rental_statement_email_message = (
                f"You haven't paid last month rent for order {order.display_order_id}, late fee applied."
            )
            charge_customer_profile_resp = None

        if is_send_email_notifications:
            statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
            email_service_mailersend.send_customer_rental_statement(
                statement['transactions_list'],
                statement['customer_detail'],
                statement['order_detail'],
                statement['company_name'],
                statement['order_info'],
                rental_statement_email_message,
            )

    # if this is not an autopay scenario, then we want the return obj to just have the orderstatus populated
    response_obj: HandleLateRentalLogicObj = HandleLateRentalLogicObj(
        order_status, charge_customer_profile_resp, periods if is_autopay else None
    )

    return response_obj


def handle_late_fee_calc(interval: timedelta, account: Account, grace_period: int) -> Decimal:
    late_fee = account.cms.get("rent_options", {}).get("late_fee", 1)
    total_late_fees_amt: Decimal = 0

    if interval.days == grace_period:
        total_late_fees_amt = grace_period * late_fee
    elif interval.days > grace_period:
        total_late_fees_amt = late_fee

    return total_late_fees_amt


@atomic()
async def handle_authorize_accounts(
    account: Account,
    api_key: str,
    trans_key: str,
    url: str,
    is_process_charges: bool,
    is_send_email_notifications: bool,
):
    orders: List[Order] = await order_crud.search_orders(
        account.id,
        status="Delivered,Delinquent",
        order_types="RENT,RENT_TO_OWN",
    )
    grace_period: int = account.cms_attributes.get("rent_options", {}).get('grace_period', 0)
    current_date: datetime = datetime.now(pytz.utc).date()
    handle_late_rental_logic_obj: HandleLateRentalLogicObj = HandleLateRentalLogicObj()

    for order in orders:
        order_status: str = ""

        # This signifies that we are in autopay
        if order.is_autopay:
            customer_profile = get_customer_profile(order.customer_profile_id, api_key, trans_key, url)
            if customer_profile.get('errorMessage'):
                logger.error(f"Error getting customer profile for order {order.display_order_id}")
                continue
            customer_payment_profile_id = customer_profile['profile']['paymentProfiles'][0]['customerPaymentProfileId']
            transactionsResponse = get_customer_profile_transactions(
                order.customer_profile_id, customer_payment_profile_id, api_key, trans_key, url
            )
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
            # today is crt_rent_period.start_date
            is_charge_day: bool = await verify_charge_day(
                order,
                account,
                latest_transaction_created,
                latest_transaction_approved,
                current_date,
                is_send_email_notifications=is_send_email_notifications,
            )

            if not latest_transaction_approved:
                # we point it to the rent period balance bc that determines if they are current or not
                # we are either going to charge them the entirety of their total balance + just accrued late fees
                handle_late_rental_logic_obj = await handle_late_rental_logic(
                    today=current_date,
                    order=order,
                    grace_period=grace_period,
                    account=account,
                    is_autopay=order.is_autopay,
                    is_process_charges=is_process_charges,
                    is_send_email_notifications=is_send_email_notifications,
                )
                order_status = handle_late_rental_logic_obj.order_status

                # if it doesnt find any outstanding periods, then it will return "" for order_status
                if order_status == "":
                    return
            # it was charge day and they have already been charged successfully
            elif is_charge_day and latest_transaction_approved:

                if is_send_email_notifications:
                    statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
                    email_service_mailersend.send_customer_rental_statement(
                        statement['transactions_list'],
                        statement['customer_detail'],
                        statement['order_detail'],
                        statement['company_name'],
                        statement['order_info'],
                        f"You have been successfully charged the monthly rent for order {order.display_order_id} today.",
                    )

        else:
            # non auto paid user
            is_charge_day = await verify_charge_day(
                order, account, None, None, current_date, is_send_email_notifications=is_send_email_notifications
            )

            handle_late_rental_logic_obj = await handle_late_rental_logic(
                today=current_date, order=order, grace_period=grace_period, account=account
            )
            order_status = handle_late_rental_logic_obj.order_status

            if is_charge_day and is_send_email_notifications:
                statement = await customer_statement_controller.generate_rental_statement(order.id, account.id)
                email_service_mailersend.send_customer_rental_statement(
                    statement['transactions_list'],
                    statement['customer_detail'],
                    statement['order_detail'],
                    statement['company_name'],
                    statement['order_info'],
                    f"You are expected to pay monthly rent for order {order.display_order_id} today.",
                )


# if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
#     handler(None, None)
