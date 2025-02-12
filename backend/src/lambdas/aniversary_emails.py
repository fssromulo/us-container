# Python imports
import asyncio

# import sys
from datetime import datetime, timezone
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
from src.controllers import order_fee_balance as fee_balance_controller
from src.controllers import orders as order_controller
from src.controllers import rent_period as rent_period_controller  # noqa: E402
from src.controllers import subtotal_balance as subtotal_balance_controller
from src.controllers import tax_balance as tax_balance_controller
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.fee_crud import fee_crud  # noqa: E402
from src.crud.order_card_info_crud import order_credit_card_crud  # noqa: E402
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.crud.tax_balance_crud import tax_balance_crud

from src.crud.order_fee_balance_crud_2 import order_fee_balance_crud_2
from src.crud.subtotal_balance_crud_2 import subtotal_balance_crud_2
from src.crud.tax_balance_crud_2 import tax_balance_crud_2


from src.crud.tax_crud import tax_crud
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account
from src.schemas.order_fee_balance import OrderFeeBalanceIn2
from src.schemas.orders import Order
from src.schemas.subtotal_balance import SubtotalBalanceIn2
from src.schemas.tax_balance import TaxBalanceIn2
from src.services.notifications.email_service import send_wrong_payments  # noqa: E402
from src.services.payment.authorize_pay_service import get_settled_batch_list, get_settled_transactions  # noqa: E402
from src.crud.note_crud import note_crud, NoteInSchema
from src.services.notifications.email_service_mailersend import (  # noqa: E402
    send_aniversary_email
)
from src.crud.notification_crud import notification_crud, NotificationIn, NotificationOut
from src.crud.notification_history_crud import notification_history_crud, NotificationHistoryIn, NotificationHistoryOut


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}

def days_between_dates(date1: datetime, date2: datetime) -> int:
    delta = date2 - date1
    return abs(delta.days)

async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    account: Account = await account_crud.get_one(1)

    current_date = datetime.now(timezone.utc)

    emails_completed_map = {}
    order_map = {}

    for account_id in [1,5]:
        skip = 0
        limit = 1000
        while True:
            orders = await order_crud.search_orders(account_id, status="Completed", pagination={"skip": skip, "limit": limit})
            if len(orders) == 0:
                break
            skip += limit
            for order in orders:
                if order.customer:
                    if order.customer.email not in emails_completed_map and order.completed_at:
                        emails_completed_map[order.customer.email] = order.completed_at
                        order_map[order.customer.email] = order
                    elif order.completed_at and order.completed_at < emails_completed_map[order.customer.email]:
                        emails_completed_map[order.customer.email] = order.completed_at
                        order_map[order.customer.email] = order

    for email in emails_completed_map:
        completed_at = emails_completed_map[email]
        days_passed = days_between_dates(completed_at, current_date)
        order = order_map[email]
        if days_passed % 365 == 0 and days_passed != 0:
            #send email

            years = int(days_passed / 365)

            notification = await notification_crud.find_notification_by_name(name = f"{years} years aniversary email")
 
            response = send_aniversary_email(account, email=email, years=int(years), notification=notification)

            await notification_history_crud.create(NotificationHistoryIn(
                order_id = order.id,
                line_item_id = None,
                user_id = None,
                notification_id = notification.id,
                notification_content = "",
                sent_by_provider = "mailersend",
                response_from_provider = str(response),
                account_id = order.account_id
            ))

            note = f"{email} - {years} aniversary - sent {current_date.isoformat()} "
            await note_crud.create(
                NoteInSchema(
                    title=note,
                    content=note,
                    author_id=None,
                    order_id=order.id
                )
            )




#if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
#   handler(None, None)
