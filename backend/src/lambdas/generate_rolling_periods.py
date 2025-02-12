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


# Python imports
from datetime import datetime

# Pip imports
import pytz

# Internal imports
from src.config import settings  # noqa: E402
from src.controllers import fee_type as fee_type_controller  # noqa: E402
from src.controllers import rent_period as rent_period_controller  # noqa: E402
from src.controllers.rent_period import generate_rent_period, generate_rolling_rent_periods
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.fee_crud import fee_crud  # noqa: E402
from src.crud.order_card_info_crud import order_credit_card_crud  # noqa: E402
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.rent_period_crud import rent_period_crud
from src.crud.user_crud import user_crud
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account
from src.schemas.payment import OtherPayment
from src.services.notifications.email_service import send_wrong_payments  # noqa: E402
from src.services.payment.authorize_pay_service import get_settled_batch_list, get_settled_transactions  # noqa: E402


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    # input parameters, order id and start date
    order_id = 'd5cd9e7d-f719-46cc-873d-2fcf9fa62d96'
    start_date = datetime(2009, 7, 17, 12, 0, 0)

    accounts: List[Account] = await account_crud.get_all()
    order = await order_crud.get_one(order_id)

    for account in accounts:
        if account.id != 2:
            continue

        rent_options: dict = account.cms_attributes.get("rent_options", {})

        rent_periods = await rent_period_crud.get_all_by_order_id(order_id)
        for rp in rent_periods:
            await rent_period_crud.delete_one(rp.id)

        is_initial_rent_period: bool = True

        amount_owed: Decimal = order.calculated_monthly_subtotal

        await generate_rent_period(amount_owed, order, rent_options, is_initial_rent_period)
        rent_periods = await rent_period_crud.get_all_by_order_id(order_id)

        #        other_payment = OtherPayment(order_id=order_id, lump_sum_amount=rent_periods[0].calculated_rent_period_total_balance)
        #        await rent_period_controller.handle_rent_period_other_pay(other_payment, order)

        end_date = datetime(2025, 5, 1, 12, 0, 0)
        order.rent_due_on_day = start_date.day
        await rent_period_controller.handle_rent_period_dates_update(rent_periods[0], order, start_date, start_date)
        rent_options['start_date'] = start_date
        rent_options['rolling_rent_periods'] = (end_date.year - start_date.year) * 12 + (
            end_date.month - start_date.month
        )

        await rent_period_controller.generate_rolling_rent_periods(rent_options, rent_periods[0], order)

        rent_periods = await rent_period_crud.get_all_by_order_id(order_id)

        sum_2 = 0
        for rp in rent_periods:
            if rp.end_date < datetime.now(pytz.utc):
                sum_2 += rp.calculated_rent_period_total_balance

        # sum_2 -= rent_periods[0].calculated_rent_period_total_balance
        other_payment = OtherPayment(order_id=order_id, lump_sum_amount=sum_2)
        order = await order_crud.get_one(order_id)
        await rent_period_controller.handle_rent_period_other_pay(other_payment, order)


if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
    handler(None, None)
