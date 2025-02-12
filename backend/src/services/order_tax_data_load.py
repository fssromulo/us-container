# Python imports
import time
from decimal import Decimal
from typing import List

# Pip imports
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401, E402
from tortoise import Tortoise  # noqa: F401, E402

# Internal imports
from src.database.tortoise_init import init_models


# enable schemas to read relationship between models
# flakes8: noqa
init_models()

# Internal imports
from src.crud.order_crud import OrderCRUD  # noqa: F401, E402
from src.crud.order_tax_crud import order_tax_crud  # noqa: F401, E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.database.models.order_tax import OrderTax  # noqa: F401, E402
from src.database.models.orders.line_item import LineItem  # noqa: E402
from src.database.models.orders.order import Order  # noqa: E402
from src.schemas.order_tax import OrderTaxIn  # noqa: F401, E402


# python imports


client = AsyncIOMotorClient()
order_crud = OrderCRUD()


async def close_orm():
    await Tortoise.close_connections()


async def populate_order_tax_table(account_id: int) -> bool:

    start_time: time = time.time()
    await Tortoise.init(config=TORTOISE_ORM)  # we need to register tortise to get everything going
    try:
        # Grab all of the orders that are either invoiced or partially paid
        orders: List[Order] = await order_crud.search_orders(
            account_id, status="Invoiced,Partially Paid,Paid,Completed,Cancelled,Delivered"
        )
    except Exception as e:
        logger.info(e)
        return False

    # logger.info(orders)
    logger.info(f"Number of orders: {len(orders)}")

    if orders:
        create_order_tax_list: List[OrderTax] = []

        for order in orders:
            create_order_tax: OrderTaxIn
            line_items: List[LineItem] = order.line_items
            total_tax: Decimal = 0

            for li in line_items:
                if li.tax != 0 and li.tax is not None:
                    total_tax += li.tax

            create_order_tax = OrderTaxIn(tax_amount=total_tax, order_id=order.id)
            create_order_tax_list.append(create_order_tax)

        try:
            if len(create_order_tax_list) > 0:
                await order_tax_crud.bulk_create(create_order_tax_list, len(create_order_tax_list))
        except Exception as e:
            raise e
        await close_orm()
        end_time: time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"\nThe process took: {elapsed_time}")
        return True
    else:
        await close_orm()
        raise Exception("There were not any orders found.")


if __name__ == "__main__":
    loop = client.get_io_loop()
    account_id: int = int(input("What is the account Id you are migrating this data for? "))
    ready_to_run: str = input("Are you ready to run the process? (Y/N): ")
    if ready_to_run.upper() == "Y":
        loop.run_until_complete(populate_order_tax_table(account_id))
    elif ready_to_run.upper() == "N":
        logger.info("Run the script again if ready")
    else:
        logger.info("Invalid input")
