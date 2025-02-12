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

def handler(event, context):
    asyncio.run(async_handler(event, context))

async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    for account_id in [1,2,3,4,5,6,7]:
        skip = 0
        limit = 1000
        while True:
            orders = await order_crud.get_all(account_id, pagination={"skip": skip, "limit": limit})
            if len(orders) == 0:
                break
            skip += limit

            transactions_to_be_deleted_ids = []
            transactions_to_be_created = []
            order_fee_balance_to_be_updated = []
            tax_balance_to_be_updated = []
            subtotal_balance_to_be_updated = []
            for order in orders:
                if order.type == 'PURCHASE' or order.type =='PURCHASE_ACCESSORY':
                    if order.credit_card:
                        for order_credit_card in order.credit_card:
                            payment_amount = order_credit_card.response_from_gateway.get("payment_amount", 0)

                            if payment_amount != 0:
                                for transaction in order_credit_card.transactions:
                                    transactions_to_be_deleted_ids.append(transaction.id)


                                transaction_type_uuid = uuid.uuid4()
                                transactions_to_be_created.append(TransactionTypeIn(
                                        id=transaction_type_uuid,
                                        created_at=order_credit_card.created_at,
                                        modified_at=datetime.now(),
                                        order_id=order.id,
                                        payment_type="CC",
                                        amount=payment_amount,
                                        account_id=order.account_id,
                                        credit_card_object_id=order_credit_card.id
                                    ))

                                for fee_balance in order_credit_card.order_fee_balance:
                                    order_fee_balance_to_be_updated.append(OrderFeeBalance(
                                                                                            id=fee_balance.id,
                                                                                            transaction_type_id=transaction_type_uuid,
                                                                                           remaining_balance=fee_balance.remaining_balance,
                                                                                           account_id=fee_balance.account_id,
                                                                                           fee_id=fee_balance.fee.id,
                                                                                           order_id=fee_balance.order_id))

                                for subtotal_balance in order_credit_card.subtotal_balance:
                                    subtotal_balance_to_be_updated.append(
                                        SubtotalBalance(
                                            id=subtotal_balance.id,
                                            transaction_type_id=transaction_type_uuid,
                                                          balance=subtotal_balance.balance,
                                                            order_id=subtotal_balance.order_id))

                                for tax_balance in order_credit_card.tax_balance:
                                    tax_balance_to_be_updated.append(
                                                 TaxBalance(
                                                     id=tax_balance.id,
                                                     transaction_type_id=transaction_type_uuid,
                                                              balance=tax_balance.balance,
                                                              tax_rate = 0,
                                                              order_id=order.id))

            await transaction_type_crud.delete_all_ids(account_id=account_id, ids=transactions_to_be_deleted_ids)
            await transaction_type_crud.bulk_create(transactions_to_be_created)
            if order_fee_balance_to_be_updated:
                await order_fee_balance_crud.bulk_update(order_fee_balance_to_be_updated, ["transaction_type_id"])
            if subtotal_balance_to_be_updated:
                await subtotal_balance_crud.bulk_update(subtotal_balance_to_be_updated, ["transaction_type_id"])
            if tax_balance_to_be_updated:
                await tax_balance_crud.bulk_update(tax_balance_to_be_updated, ["transaction_type_id"])


handler(None, None)
