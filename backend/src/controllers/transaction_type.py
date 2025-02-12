# Python imports
import uuid
from decimal import Decimal
from typing import List

# Pip imports
# from fastapi import HTTPException, status
# from tortoise import Model
# from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import balance as balance_controller
from src.controllers.event_controller import send_event
from src.crud.fee_crud import fee_crud
from src.crud.note_crud import NoteInSchema, note_crud
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.crud.rent_period_balance_crud import RentPeriodBalanceIn, rent_period_balance_crud
from src.crud.rent_period_crud import RentPeriod, rent_period_crud
from src.crud.rent_period_fee_balance_crud import RentPeriodFeeBalanceIn, rent_period_fee_balance_crud
from src.crud.rent_period_tax_balance_crud import RentPeriodTaxBalanceIn, rent_period_tax_balance_crud
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.crud.tax_balance_crud import tax_balance_crud
from src.crud.transaction_type_crud import transaction_type_crud
from src.database.models.orders.order import Order
from src.database.models.transaction_type import TransactionType
from src.schemas.order_fee_balance import OrderFeeBalanceIn
from src.schemas.subtotal_balance import SubtotalBalanceIn
from src.schemas.tax_balance import TaxBalanceIn
from src.schemas.token import Status
from src.schemas.transaction_type import (
    TransactionTypeIn,
    TransactionTypeInDto,
    TransactionTypeInUpdate,
    TransactionTypeOut,
)
from src.utils.utility import make_json_serializable


async def create_transaction_type(
    transaction_type: TransactionTypeIn, user: Auth0User, background_tasks=None
) -> TransactionTypeOut:
    transaction_type.group_id = str(uuid.uuid4())
    transaction_type.account_id = user.app_metadata['account_id']
    saved_transaction_type = await transaction_type_crud.create(transaction_type)

    # send event to event controller
    if background_tasks:
        background_tasks.add_task(
            send_event,
            user.app_metadata['account_id'],
            str(saved_transaction_type.order_id),
            make_json_serializable(
                {
                    "payment_method": saved_transaction_type.payment_type,
                    "transaction_date": saved_transaction_type.created_at,
                    "success": True,
                }
            ),
            "payment",
            "make_payment",
        )

    return saved_transaction_type


async def get_transaction_types_grouped(id, user):
    tt = await transaction_type_crud.get_one_without_account(id)
    if tt.group_id:
        return await transaction_type_crud.get_transaction_types_by_group_id(tt.group_id)
    else:
        return [tt]


@atomic()
async def update_transaction_type(
    transaction_id: str, transaction_type: TransactionTypeInDto, user: Auth0User
) -> TransactionTypeOut:
    old_item: TransactionType = await transaction_type_crud.get_one(
        user.app_metadata.get("account_id"), item_id=transaction_id
    )

    if old_item.group_id is None:
        updated_transaction_type = await transaction_type_crud.update(
            user.app_metadata.get("account_id"),
            transaction_id,
            TransactionTypeInUpdate(**transaction_type.dict(exclude_unset=True)),
        )
    else:
        tts = await transaction_type_crud.get_transaction_types_by_group_id(old_item.group_id)
        for tt in tts:
            updated_transaction_type = await transaction_type_crud.update(
                user.app_metadata.get("account_id"),
                tt.id,
                TransactionTypeInUpdate(
                    **transaction_type.dict(exclude_unset=True)
                ),
            )
    return updated_transaction_type


async def get_transaction_type(transaction_id: str, user: Auth0User) -> TransactionTypeOut:
    transaction_type = await transaction_type_crud.get_one(user.app_metadata.get("account_id"), transaction_id)
    return transaction_type


async def get_order_transaction_types(order_id: str, user: Auth0User) -> List[TransactionTypeOut]:
    return await transaction_type_crud.db_model.filter(order_id=order_id)


async def get_period_transaction_types(rent_period_id: str, user: Auth0User) -> List[TransactionTypeOut]:
    return await transaction_type_crud.db_model.filter(rent_period_id=rent_period_id)

@atomic()
async def delete_transaction_type(transaction_id, user: Auth0User) -> Status:
    old_item: TransactionType = await transaction_type_crud.get_one_without_account(transaction_id)
    adjustment: Decimal = Decimal(old_item.amount)

    if old_item.order_id is not None:
        order = await order_crud.get_one(old_item.order_id, False)

        await balance_controller.order_balance_adjustment(order, abs(adjustment), True)

        await recalculated_balances(order, old_item)
        await transaction_type_crud.delete_without_account(transaction_id)

    else:
        tts = []
        if old_item.group_id is not None:
            tts = await transaction_type_crud.get_transaction_types_by_group_id(old_item.group_id)
        else:
            tts = [old_item]
        for old_item in tts:
            rent_period = await rent_period_crud.get_one(old_item.rent_period.id)

            await balance_controller.rent_period_total_balance_adjustment(rent_period, abs(adjustment), True)
            await recalculate_rental_balances(rent_period, old_item)

            rent_period: RentPeriod = await rent_period_crud.get_one(old_item.rent_period.id)

            note = f"{user.email} deleted this transaction. "
            note += f"This transaction_type was {old_item.payment_type} and the amount was {old_item.amount}."
            await note_crud.create(
                NoteInSchema(
                    title=note,
                    content=note,
                    author_id=user.id.replace("auth0|", ""),
                    order_id=rent_period.order_id,
                )
            )
            await transaction_type_crud.delete_without_account(old_item.id)

    return Status(message="Removed transaction type")


async def recalculate_rental_balances(existing_rent_period: RentPeriod, transaction_type: TransactionType):
    rent_period_balances = await rent_period_balance_crud.get_by_rental_id(existing_rent_period.id)
    rent_period_fee_balances = await rent_period_fee_balance_crud.get_by_rental_id(existing_rent_period.id)
    rent_period_tax_balances = await rent_period_tax_balance_crud.get_by_rental_id(existing_rent_period.id)

    prev_balance = None
    crt_balance = None
    rent_period_balance_amount = 0
    for tsb in rent_period_balances:
        prev_balance = crt_balance
        crt_balance = tsb

        if tsb.transaction_type and tsb.transaction_type.id == transaction_type.id:
            if prev_balance:
                rent_period_balance_amount += prev_balance.remaining_balance - crt_balance.remaining_balance

    if rent_period_balance_amount > 0:
        await rent_period_balance_crud.create(
            RentPeriodBalanceIn(
                remaining_balance=existing_rent_period.calculated_rent_period_balance + rent_period_balance_amount,
                rent_period_id=existing_rent_period.id,
            )
        )

    prev_balance = None
    crt_balance = None
    rent_period_fee_balance_amount = 0
    for tsb in rent_period_fee_balances:
        prev_balance = crt_balance
        crt_balance = tsb

        if tsb.transaction_type and tsb.transaction_type.id == transaction_type.id:
            if prev_balance:
                rent_period_fee_balance_amount += prev_balance.remaining_balance - crt_balance.remaining_balance

    if rent_period_fee_balance_amount > 0:
        await rent_period_fee_balance_crud.create(
            RentPeriodFeeBalanceIn(
                remaining_balance=existing_rent_period.calculated_rent_period_fee_balance
                + rent_period_fee_balance_amount,
                rent_period_id=existing_rent_period.id,
            )
        )

    prev_balance = None
    crt_balance = None
    rent_period_tax_balance_amount = 0
    for tsb in rent_period_tax_balances:
        prev_balance = crt_balance
        crt_balance = tsb

        if tsb.transaction_type and tsb.transaction_type.id == transaction_type.id:
            if prev_balance:
                rent_period_tax_balance_amount += prev_balance.balance - crt_balance.balance

    if rent_period_tax_balance_amount > 0:
        await rent_period_tax_balance_crud.create(
            RentPeriodTaxBalanceIn(
                balance=existing_rent_period.calculated_rent_period_tax_balance + rent_period_tax_balance_amount,
                rent_period_id=existing_rent_period.id,
                tax_rate=0,
            )
        )


async def recalculated_balances(existing_order: Order, transaction_type: TransactionType):
    subtotal_balances = await subtotal_balance_crud.get_by_order_id(existing_order.id)
    transaction_subtotal_balances = sorted(subtotal_balances, key=lambda x: x.created_at)

    prev_balance = None
    crt_balance = None
    subtotal_sum_amount = 0
    for tsb in transaction_subtotal_balances:
        prev_balance = crt_balance
        crt_balance = tsb

        if tsb.transaction_type_id == transaction_type.id:
            subtotal_sum_amount += prev_balance.balance - crt_balance.balance

    if subtotal_sum_amount > 0:
        await subtotal_balance_crud.create(
            SubtotalBalanceIn(
                balance=existing_order.calculated_order_subtotal_balance + subtotal_sum_amount,
                order_id=existing_order.id,
            )
        )

    tax_balances = await tax_balance_crud.get_by_order_id(existing_order.id)
    transaction_tax_balances = sorted(tax_balances, key=lambda x: x.created_at)

    prev_balance = 0
    crt_balance = 0
    tax_sum_amount = 0
    for tsb in transaction_tax_balances:
        prev_balance = crt_balance
        crt_balance = tsb

        if tsb.transaction_type_id == transaction_type.id:
            tax_sum_amount += prev_balance.balance - crt_balance.balance

    if tax_sum_amount > 0:
        await tax_balance_crud.create(
            TaxBalanceIn(
                balance=existing_order.calculated_order_tax_balance + tax_sum_amount,
                order_id=existing_order.id,
                tax_rate=0,
            )
        )

    order_fee_balances = await order_fee_balance_crud.get_by_order_id(existing_order.id)
    transaction_order_fee_balances = sorted(order_fee_balances, key=lambda x: x.created_at)

    fee_ids_set = {}
    for tsb in transaction_order_fee_balances:
        fee_ids_set[tsb.fee_id] = await fee_crud.get_one(existing_order.account_id, tsb.fee_id)

    for fee_id, fee in fee_ids_set.items():
        crt_fee_id_balances = [x for x in transaction_order_fee_balances if x.fee_id == fee_id]

        fee_amount = 0
        prev_balance = None
        crt_balance = None
        for tsb in crt_fee_id_balances:
            prev_balance = crt_balance
            crt_balance = tsb

            if tsb.transaction_type_id == transaction_type.id:
                fee_amount = prev_balance.remaining_balance - crt_balance.remaining_balance

        if fee_amount > 0:
            await order_fee_balance_crud.create(
                OrderFeeBalanceIn(
                    remaining_balance=fee.calculated_remaining_balance + fee_amount,
                    order_id=existing_order.id,
                    fee_id=fee_id,
                    account_id=existing_order.account_id,
                )
            )
