# Python imports
import asyncio

# import sys
from typing import List

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
from src.crud.rent_period_tax_balance_crud import rent_period_tax_balance_crud  # noqa: E402
from src.crud.rent_period_tax_crud import rent_period_tax_crud  # noqa: E402
from src.crud.rent_period_total_balance_crud import rent_period_total_balance_crud  # noqa: E402
from src.crud.tax_crud import tax_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.rent_period import RentPeriod  # noqa: E402
from src.schemas.rent_period_balance import RentPeriodBalanceIn  # noqa: E402
from src.schemas.rent_period_tax import RentPeriodTaxIn  # noqa: E402
from src.schemas.rent_period_tax_balance import RentPeriodTaxBalanceIn  # noqa: E402
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn  # noqa: E402


def handler(event, context):
    asyncio.run(async_handler(event, context))


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    display_order_id = "332187"
    account_id = 1
    new_rental_price = 50
    logger.info("Getting all order ids that havea balance")
    order = await order_crud.get_one_by_display_id(account_id, display_order_id)
    tax_states = [line_item.product_state for line_item in order.line_items if line_item.product_state]

    if tax_states:
        tax_rate = await tax_crud.get_tax_rate(order.account_id, tax_states[0])
    else:
        tax_rate = 0.0

    period_update: List[RentPeriod] = []
    period_balance: List[RentPeriodBalanceIn] = []
    tax_balance: List[RentPeriodTaxBalanceIn] = []
    tax: List[RentPeriodTaxIn] = []
    period_total_balance: List[RentPeriodTotalBalanceIn] = []
    for period in order.rent_periods:
        amount_owed = period.amount_owed - new_rental_price
        period_update.append(RentPeriod(amount_owed=new_rental_price, id=period.id))
        # This should reflect in the period balance as well
        pb = period.calculated_rent_period_balance - amount_owed
        period_balance.append(RentPeriodBalanceIn(remaining_balance=pb, rent_period_id=period.id))

        pb = period.calculated_rent_period_total_balance - (amount_owed + tax_rate * amount_owed)
        period_total_balance.append(RentPeriodTotalBalanceIn(remaining_balance=pb, rent_period_id=period.id))

        pb = period.calculated_rent_period_tax_balance - tax_rate * amount_owed
        tax_balance.append(RentPeriodTaxBalanceIn(balance=pb, tax_rate=0, rent_period_id=period.id))

        pb = period.calculated_rent_period_tax - tax_rate * amount_owed
        tax.append(RentPeriodTaxIn(tax_amount=pb, rent_period_id=period.id))

    if len(period_update) > 0:
        await rent_period_crud.bulk_update(period_update, ['amount_owed'], len(period_update))
        await rent_period_balance_crud.bulk_create(period_balance, len(period_balance))
        await rent_period_total_balance_crud.bulk_create(period_total_balance, len(period_total_balance))
        await rent_period_tax_balance_crud.bulk_create(tax_balance, len(tax_balance))
        await rent_period_tax_crud.bulk_create(tax, len(tax))


handler(None, None)
