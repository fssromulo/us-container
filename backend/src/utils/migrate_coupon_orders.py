# Python imports
import sys
from typing import List

# Pip imports
from loguru import logger


sys.path.append("..")

# Python imports
import time  # noqa: F401, E402

# Pip imports
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401, E402
from tortoise import Tortoise  # noqa: F401, E402

# Internal imports
from src.crud.coupon_code_crud import coupon_code_crud  # noqa: F401, E402
from src.crud.coupon_line_item_value_crud import coupon_line_item_crud  # noqa: F401, E402
from src.crud.order_crud import order_crud  # noqa: F401, E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.schemas.coupon_line_item_value import CouponLineItemValueIn  # noqa: F401, E402


client = AsyncIOMotorClient()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortise():
    logger.info("registering tortoise")

    await Tortoise.init(config=TORTOISE_ORM)


async def main():
    await register_tortise()
    # Step 1 Fetch all orders with coupons
    # accounts: List[Account] = await account_crud.get_all()
    coupon_orders: List = []
    all_coupons = await coupon_code_crud.get_all(1)
    for coupon in all_coupons:
        orders = await order_crud.orders_with_coupon_id(1, coupon.id)
        # For each line item that meets the minimum threshold create a coupon_line_item_value list item using the coupon amount
        for order in orders:
            if order.coupon_code_order is not None and order.line_items is not None:
                for code_order in order.coupon_code_order:
                    for line_item in order.line_items:
                        if (
                            line_item.revenue >= coupon.minimum_discount_threshold
                            and line_item.product_type != "CONTAINER_ACCESSORY"
                        ):
                            coupon_dict = {
                                "line_item_id": line_item.id,
                                "coupon_code_order_id": code_order.id,
                                "amount": coupon.amount,
                            }

                            coupon_orders.append(CouponLineItemValueIn(**coupon_dict))
    # Save the list
    logger.info(coupon_orders)
    await coupon_line_item_crud.bulk_create(coupon_orders, len(coupon_orders))
    await close_orm()
    sys.exit(1)


if __name__ == "__main__":
    # # Python imports
    # import asyncio
    loop = client.get_io_loop()
    loop.run_until_complete(main())
