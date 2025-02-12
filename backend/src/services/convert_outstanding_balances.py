# Pip imports
from loguru import logger
from tortoise import Tortoise  # noqa: F401, E402

# Internal imports
from src.database.tortoise_init import init_models


# enable schemas to read relationship between models
# flakes8: noqa
init_models()

# Python imports
import time  # noqa: E402

# python imports
from decimal import Decimal  # noqa: E402
from typing import List, Union  # noqa: E402

# Pip imports
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401, E402

# Internal imports
from src.crud.fee_crud import fee_crud  # noqa: E402
from src.crud.order_crud import OrderCRUD  # noqa: E402
from src.crud.total_order_balance_crud import total_order_balance_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.database.models.fee import Fee  # noqa: E402
from src.database.models.fee_type import FeeType  # noqa: E402
from src.database.models.orders.order import Order  # noqa: E402
from src.database.models.orders_status import OrderStatus  # noqa: E402
from src.schemas.fee import FeeIn  # noqa: E402
from src.schemas.total_order_balance import TotalOrderBalanceIn  # noqa: E402


client = AsyncIOMotorClient()
order_crud = OrderCRUD()


async def close_orm():
    await Tortoise.close_connections()


async def summing_fees(order: Order) -> Union[Fee, None]:
    """
    Calculate the sum of convenience fees from a list of line items and return a single FeeIn object to be inserted elsewhere

    :param order_id: The ID of the order associated with the fees.

    :return: If the total fees are greater than 0, a FeeIn object is returned. Otherwise, None is returned.
    """
    try:
        # sum up each of their convenience_fee columns only for the ones that have convenience fees in them
        total_fees: Decimal = sum(
            [line_item.convenience_fee for line_item in order.line_items if line_item.convenience_fee]
        )
    except Exception as e:
        raise e
    if total_fees > 0:
        # insert this lump sum into the fee table
        create_fee = FeeIn(fee_amount=total_fees, fee_type=FeeType.CREDIT_CARD, order_id=order.id)
        return create_fee


async def migrate_existing_orders(account_id: int) -> bool:
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
        create_order_balance_list: List[TotalOrderBalanceIn] = []
        create_fee_list: List[FeeIn] = []

        new_remaining_balance: Decimal = 0
        create_order_balance: TotalOrderBalanceIn
        for order in orders:
            if order.status == OrderStatus.INVOICED:
                # Grab the total price
                new_remaining_balance = order.total_price

                # Insert that into order_balance table
                create_order_balance = TotalOrderBalanceIn(remaining_balance=new_remaining_balance, order_id=order.id)
                create_order_balance_list.append(create_order_balance)
                # await total_order_balance_crud.create(create_order_balance)

            elif order.status == OrderStatus.PARTIALLY_PAID:
                # Grab the current remaining balance
                new_remaining_balance = order.remaining_balance

                # insert it into the order_balance table
                create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
                    remaining_balance=new_remaining_balance, order_id=order.id
                )
                create_order_balance_list.append(create_order_balance)

                try:
                    fee_in: Union[FeeIn, None] = await summing_fees(order)
                    if fee_in is not None:
                        create_fee_list.append(fee_in)
                except Exception as e:
                    logger.info(e)
                    return False

            # this would be Paid, Completed, Cancel, and Delivered
            # and here we do not need to touch anything with the remaining balance
            # we only need to add the bank fees if there are any
            else:
                try:
                    fee_in: Union[FeeIn, None] = await summing_fees(order)
                    if fee_in is not None:
                        create_fee_list.append(fee_in)
                except Exception as e:
                    logger.info(e)
                    return False

        try:
            if len(create_order_balance_list) > 0:
                await total_order_balance_crud.bulk_create(create_order_balance_list, len(create_order_balance_list))
            if len(create_fee_list) > 0:
                await fee_crud.bulk_create(create_fee_list, len(create_fee_list))
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
        loop.run_until_complete(migrate_existing_orders(account_id))
    elif ready_to_run.upper() == "N":
        logger.info("Run the script again if ready")
    else:
        logger.info("Invalid input")
