# Python imports
import asyncio

# import sys
import datetime
from decimal import Decimal
from typing import List

# Pip imports
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models


# enable schemas to read relationship between models
# flakes8: noqa
init_models()


# Internal imports
from src.config import settings  # noqa: E402
from src.controllers import fee_type as fee_type_controller  # noqa: E402
from src.controllers import rent_period as rent_period_controller  # noqa: E402
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.fee_crud import fee_crud  # noqa: E402
from src.crud.order_card_info_crud import order_credit_card_crud  # noqa: E402
from src.crud.order_crud import order_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account
from src.services.notifications.email_service import send_wrong_payments  # noqa: E402
from src.services.payment.authorize_pay_service import get_settled_batch_list, get_settled_transactions  # noqa: E402


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    accounts: List[Account] = await account_crud.get_all()

    for account in accounts:
        authorize_int_purchase = account.integrations.get("authorize", {}).get("purchase", {})

        if authorize_int_purchase.get("in_use"):
            await handle_authorize_accounts(
                account,
                authorize_int_purchase['api_login_id'],
                authorize_int_purchase["transaction_key"],
                url=authorize_int_purchase["url"],
            )


async def handle_authorize_accounts(account: Account, api_key: str, trans_key: str, url: str):
    convenience_percentage = account.cms_attributes.get("convenience_fee_rate", 0)

    today_date = datetime.date.today()

    two_days_ago = today_date - datetime.timedelta(days=2)

    start_time = datetime.datetime.combine(two_days_ago, datetime.time(0, 1))
    end_time = datetime.datetime.combine(two_days_ago, datetime.time(23, 59))

    order_credit_card_list = await order_credit_card_crud.get_all_between_dates(account.id, start_time, end_time)

    orders = []
    orders_in_paid_status_declined = []
    for order_credit_card in order_credit_card_list:
        order_id = order_credit_card.order_id

        try:
            order = await order_crud.get_one(order_id)
        except:
            continue

        if (order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY') and order.account_id == account.id:
            orders.append(order)

            if order.status in ['Paid', 'Partially Paid'] and order_credit_card.response_from_gateway.get(
                'errorMessage'
            ):
                orders_in_paid_status_declined.append(order.display_order_id)

    settled_orders = {}
    batch_list = get_settled_batch_list(start_time, end_time, api_key, trans_key, url)
    for batch in batch_list.get('batchList', []):
        batch_id = batch['batchId']

        transactions = get_settled_transactions(batch_id, api_key, trans_key, url)

        for transaction in transactions['transactions']:
            for order in orders:
                if transaction.get('invoiceNumber') == order.display_order_id:
                    result = abs(
                        Decimal(transaction['settleAmount'])
                        - Decimal(order.calculated_sub_total_price) * Decimal(1.0 + convenience_percentage)
                    )

                    if result > 1:
                        settled_orders[order.id] = {
                            "display_order_id": order.display_order_id,
                            "margin_of_error": result,
                        }
                    else:
                        settled_orders[order.id] = {"display_order_id": order.display_order_id, "margin_of_error": 0}

    not_settled_orders = {}
    for order in orders:
        if order.id not in not_settled_orders and order.id not in settled_orders:
            not_settled_orders[order.id] = {"display_order_id": order.display_order_id}

    send_wrong_payments(settled_orders, not_settled_orders, orders_in_paid_status_declined, account)


#   if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
#       handler(None, None)
