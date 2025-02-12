# Python imports
import asyncio
from datetime import datetime, timedelta
import traceback
import sys

# Pip imports
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.crud.account_crud import account_crud
from src.crud.order_crud import OrderCRUD
from src.database.config import TORTOISE_ORM
from src.database.models.orders.order import Order
from src.database.tortoise_init import init_models
from src.crud.partial_order_crud import partial_order_crud
from src.services.notifications import email_service_mailersend  # noqa: E402

# sys.path.append("..")


# enable schemas to read relationship between models
# flakes8: noqa
init_models()

order_crud = OrderCRUD()


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    now = datetime.now()
    accounts = await account_crud.get_all()
    for account in accounts:
        expire_days = account.cms_attributes.get("order_expire_days", 0)

        if expire_days != 0:
            # Set start date to far back to cover all orders and end date to 6 days ago
            start_date = datetime.min
            end_date = now - timedelta(days=expire_days + 1, hours=6)

            try:
                orders = await partial_order_crud.search_orders(
                    account_id=account.id,
                    created_at=True,
                    start_date=start_date.strftime("%m/%d/%y"),
                    end_date=end_date.strftime("%m/%d/%y"),
                    status="Invoiced",
                )
            except Exception as e:
                await email_service_mailersend.send_exception_email("expire_orders", str(''.join(traceback.format_exception(*sys.exc_info()))))

            logger.info(f"About to expire {len(orders)} orders")
            orders_to_expire = []
            for order in orders:
                set_order = {"id": order.id, "status": "Expired"}
                orders_to_expire.append(Order(**set_order))
                logger.info(f"{order.display_order_id} To Expire")
            try:
                result = await Order.bulk_update(orders_to_expire, ['status'], 500)
            except Exception as e:
                await email_service_mailersend.send_exception_email("expire_orders", str(''.join(traceback.format_exception(*sys.exc_info()))))
            logger.info(f"Expired {result} orders")
    return 'Success'
