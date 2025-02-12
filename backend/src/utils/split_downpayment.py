# Python imports
import asyncio
import uuid

# import sys
from decimal import Decimal
from datetime import datetime

# Pip imports
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models
from tortoise.transactions import atomic

init_models()

# Internal imports
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.rent_period_balance_crud import rent_period_balance_crud  # noqa: E402
from src.crud.rent_period_crud import rent_period_crud  # noqa: E402
from src.crud.total_order_balance_crud import total_order_balance_crud  # noqa: E402
from src.crud.transaction_type_crud import transaction_type_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.schemas.transaction_type import TransactionTypeIn, TransactionType  # noqa: E402
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_crud import order_crud
from src.crud.order_fee_balance_crud import order_fee_balance_crud, OrderFeeBalanceIn, OrderFeeBalance
from src.crud.subtotal_balance_crud import subtotal_balance_crud, SubtotalBalanceIn, SubtotalBalance
from src.crud.tax_balance_crud import tax_balance_crud, TaxBalanceIn, TaxBalance
from src.crud.account_crud import account_crud
from src.controllers.rent_period import generate_rent_period
from src.crud.rent_period_fee_crud import rent_period_fee_crud
from src.controllers import fee_type as fee_type_controller
from src.crud.fee_type_crud import FeeType
from src.crud.rent_period_fee_crud import rent_period_fee_crud, RentPeriodFeeIn

def handler(event, context):
    asyncio.run(async_handler(event, context))

async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    
    for account_id in [2]:
        skip = 0
        limit = 1000
        while True:
            orders = await order_crud.search_orders(
                account_id=account_id,
                order_types=['RENT'],
                pagination={"skip": skip, "limit": limit})
            if len(orders) == 0:
                break
            skip += limit

            delete_all_fee_ids = []
            create_rent_period_fees = []


            for order in orders:
                if order.rent_periods and  order.rent_periods[0].rent_period_fees:
                    description = order.rent_periods[0].rent_period_fees[0].description
                    if  "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP" == description \
                            and ( order.rent_periods[0].rent_period_fees[0].fee_type == 'FIRST_PAYMENT' or order.rent_periods[0].rent_period_fees[0].fee_type is None):
                                delete_all_fee_ids.append(order.rent_periods[0].rent_period_fees[0].id)

                                drop_off_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "DROP_OFF")

                                create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
                                    fee_amount=order.rent_periods[0].rent_period_fees[0].fee_amount/2,
                                    type_id=drop_off_fee_type.id,
                                    description=description + " new",
                                    rent_period_id=order.rent_periods[0].id,
                                )
                                create_rent_period_fees.append(create_rent_period_fee)

                                pickup_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "PICK_UP")

                                create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
                                    fee_amount=order.rent_periods[0].rent_period_fees[0].fee_amount/2,
                                    type_id=pickup_fee_type.id,
                                    description=description + " new",
                                    rent_period_id=order.rent_periods[0].id,
                                )
                                create_rent_period_fees.append(create_rent_period_fee)
                    elif  "FIRST_MONTH_PLUS_DELIVERY" == description \
                            and ( order.rent_periods[0].rent_period_fees[0].fee_type == 'FIRST_PAYMENT' or order.rent_periods[0].rent_period_fees[0].fee_type is None):
                                delete_all_fee_ids.append(order.rent_periods[0].rent_period_fees[0].id)

                                drop_off_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "DROP_OFF")

                                create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
                                    fee_amount=order.rent_periods[0].rent_period_fees[0].fee_amount,
                                    type_id=drop_off_fee_type.id,
                                    description=description + " new",
                                    rent_period_id=order.rent_periods[0].id,
                                )
                                create_rent_period_fees.append(create_rent_period_fee)


            await rent_period_fee_crud.bulk_create(create_rent_period_fees)
            await rent_period_fee_crud.delete_all_ids_without_account(account_id=account_id, ids=delete_all_fee_ids)


handler(None, None)
