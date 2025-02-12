# Python imports
import asyncio
import uuid

# import sys
from decimal import Decimal

# Pip imports
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models


init_models()

# Internal imports
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.rent_period_balance_crud import rent_period_balance_crud  # noqa: E402
from src.crud.rent_period_crud import rent_period_crud  # noqa: E402
from src.crud.total_order_balance_crud import total_order_balance_crud  # noqa: E402
from src.crud.transaction_type_crud import transaction_type_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.schemas.transaction_type import TransactionTypeIn  # noqa: E402


def handler(event, context):
    asyncio.run(async_handler(event, context))


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    logger.info("Getting all order ids that havea balance")
    order_ids = await total_order_balance_crud.get_distinct_order_ids()

    logger.info("Getting all orders")
    orders = await order_crud.get_by_ids(order_ids)

    transasction_types_list = []
    # Purchase orders
    for order in orders:
        logger.info(f"order id {order.display_order_id}")
        # order = await order_crud.get_one_without_exception(order_id)

        if not order:
            continue

        if order.type != 'PURCHASE' and order.type != 'PURCHASE_ACCESSORY':
            continue

        calculated_total_price = order.calculated_total_price
        order_balances = order.order_balance
        order_balances = sorted(order_balances, key=lambda x: x.created_at, reverse=False)

        diff_sum = 0
        transaction_amounts = []
        for i in range(len(order_balances)):
            if i == 0:
                diff_sum = calculated_total_price - Decimal(order_balances[0].remaining_balance)
            else:
                diff_sum = order_balances[i - 1].remaining_balance - order_balances[i].remaining_balance

            if diff_sum > 0:
                transaction_amounts.append(diff_sum)

        logger.info(f"transasction_amounts {transaction_amounts}")

        for amount in transaction_amounts:
            if order.payment_type == "CC" or order.status in ["Invoiced", "Expired"]:
                continue
            transasction_types_list.append(
                TransactionTypeIn(
                    payment_type=order.payment_type if order.payment_type is not None else "Echeck",
                    order_id=order.id,
                    amount=Decimal(amount),
                    group_id=uuid.uuid4(),
                    notes="Added from script",
                    account_id=order.account_id,
                    created_at=order.paid_at if order.paid_at is not None else order.created_at,
                )
            )

    logger.info("Bulk creating transaction types")
    await transaction_type_crud.bulk_create(transasction_types_list, len(transasction_types_list))

    rent_period_ids = await rent_period_balance_crud.get_distinct_rent_period_ids()
    rent_periods = await rent_period_crud.get_by_ids(rent_period_ids)
    rent_periods_transasction_types_list = []
    # Purchase orders
    for rent_period in rent_periods:
        logger.info(f"rent period id {rent_period.id}")

        if not rent_period:
            continue

        ammount_owed = rent_period.amount_owed
        rent_period_balances = rent_period.rent_period_balances
        rent_period_balances = sorted(rent_period_balances, key=lambda x: x.created_at, reverse=False)

        diff_sum = 0
        transaction_amounts = []
        for i in range(len(rent_period_balances)):
            if i == 0:
                diff_sum = ammount_owed - Decimal(rent_period_balances[0].remaining_balance)
            else:
                diff_sum = rent_period_balances[i - 1].remaining_balance - rent_period_balances[i].remaining_balance

            if diff_sum > 0:
                transaction_amounts.append(diff_sum)

        for amount in transaction_amounts:
            if order.status in ["Invoiced", "Expired"]:
                continue
            rent_periods_transasction_types_list.append(
                TransactionTypeIn(
                    payment_type=order.payment_type if order.payment_type is not None else "Echeck",
                    rent_period_id=rent_period.id,
                    amount=Decimal(amount),
                    group_id=uuid.uuid4(),
                    notes="Added from script",
                    account_id=order.account_id,
                    created_at=order.paid_at if order.paid_at is not None else order.created_at,
                )
            )

    logger.info("Bulk creating transaction types")
    await transaction_type_crud.bulk_create(
        rent_periods_transasction_types_list, len(rent_periods_transasction_types_list)
    )


handler(None, None)
