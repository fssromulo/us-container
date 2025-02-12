# Python imports
from decimal import Decimal
from typing import List

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import balance as balance_controller
from src.controllers import order_fee_balance as order_fee_balance_controller
from src.crud.fee_crud import fee_crud
from src.crud.note_crud import note_crud
from src.crud.order_crud import order_crud
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.database.models.fee import Fee
from src.database.models.fee_type import FeeType
from src.database.models.orders.order import Order
from src.schemas.accounts import Account
from src.schemas.fee import FeeIn, UpdateFee
from src.schemas.notes import NoteInSchema
from src.schemas.order_fee_balance import OrderFeeBalanceIn
from src.schemas.token import Status
from tortoise.transactions import atomic

@atomic()
async def create_fee(
    fee: List[FeeIn], user: Auth0User, account: Account, quick_sale_override_tax: bool = False
) -> Status:
    # test
    createdFees: List[Fee] = await fee_crud.db_model.bulk_create([fee_crud.db_model(**f.dict()) for f in fee])
    order_id: str = fee[0].order_id
    existing_order: Order = await order_crud.get_one(order_id)
    feeTypes: List[FeeType] = await FeeType.filter(id__in=[currentFee.type_id for currentFee in createdFees])
    update_fees_list: List[OrderFeeBalanceIn] = []

    # grab sum of fees
    sum_of_fees: Decimal = sum(fee.fee_amount for fee in createdFees)
    fee_to_be_taxed: Decimal = 0
    new_fee_tax: Decimal = 0
    hasRushFee = False
    for g in createdFees:
        update_fees_list.append(
            OrderFeeBalanceIn(
                remaining_balance=g.fee_amount,
                order_id=existing_order.id,
                account_id=existing_order.account_id,
                fee_id=g.id,
            )
        )
        if g.fee_type == 'RUSH':
            hasRushFee = True
            break

    for f in feeTypes:
        if f.is_taxable:
            for g in createdFees:
                if g.type_id == f.id:
                    fee_to_be_taxed += g.fee_amount

    if account.cms_attributes.get("charge_tax", True) and not quick_sale_override_tax:
        if fee_to_be_taxed != 0:
            new_fee_tax = await balance_controller.handle_order_tax_calc(existing_order, fee_to_be_taxed, True)

    if hasRushFee:
        await note_crud.create(
            NoteInSchema(
                title="Rush Fee Applied",
                content="Rush Fee was applied",
                author_id=user.app_metadata.get("id"),
                order_id=order_id,
            )
        )

    total_amount_change: Decimal = sum_of_fees + new_fee_tax

    await balance_controller.order_balance_adjustment(existing_order, total_amount_change, True)

    await order_fee_balance_controller.handle_initial_fee_balance(update_fees_list)
    return Status(message="Fee(s) created")

@atomic()
async def update_fee(fee: List[UpdateFee], user: Auth0User, account: Account) -> Status:
    update_fees_list: List[Fee] = []
    update_fees_balance_list: List[OrderFeeBalanceIn] = []
    total_order_balance_change: Decimal = 0
    fees_amount: Decimal = 0
    order_id: str = fee[0].order_id
    existing_order: Order = await order_crud.get_one(order_id)
    for f in fee:
        copy_fee = f.copy()
        fees_amount += Decimal(copy_fee.order_balance_change)
        update_fees_balance_list.append(
            OrderFeeBalanceIn(
                remaining_balance=copy_fee.updated_balance_change,
                order_id=copy_fee.order_id,
                account_id=account.id,
                fee_id=copy_fee.id,
            )
        )
        del copy_fee.order_balance_change
        del copy_fee.updated_balance_change
        new_fee = Fee(**copy_fee.dict())
        # had to alter this back to the original f.fee_type because with the enumerator
        # it KEPT THROWING AN ERROR saying tortoise.exceptions.OperationalError: column "late" does not exist
        # or whatever else you tried to update it with. It has something to do with the enum
        # that made the update feel like we were using it as a column. Works now
        new_fee.fee_type = copy_fee.fee_type
        update_fees_list.append(new_fee)
    await Fee.bulk_update(update_fees_list, ['fee_amount', 'type_id'], len(update_fees_list))
    await order_fee_balance_controller.handle_initial_fee_balance(update_fees_balance_list)

    feeTypes: List[FeeType] = await FeeType.filter(id__in=[currentFee.type_id for currentFee in fee])
    # need to know if we need to update the order balance. so have to check if fee_amount is in there
    taxable_fees_total: Decimal = 0
    total_order_balance_change = fees_amount
    fee_tax_change: Decimal = 0
    if total_order_balance_change != 0.0:
        is_adding: bool = total_order_balance_change > 0

        for f in feeTypes:
            if f.is_taxable:
                for g in fee:
                    if g.type_id == str(f.id):
                        taxable_fees_total += g.order_balance_change

        if account.cms_attributes.get("charge_tax", True):
            if taxable_fees_total != 0:
                fee_tax_change = await balance_controller.handle_order_tax_calc(
                    existing_order, taxable_fees_total, is_adding
                )

        total_order_balance_change += fee_tax_change

        await balance_controller.order_balance_adjustment(existing_order, total_order_balance_change, is_adding)

    return Status(message="Fees updated")

@atomic()
async def delete_fee(fee_id: str, user: Auth0User, account: Account) -> Status:
    fee: Fee = await fee_crud.get_one(user.app_metadata.get("account_id"), fee_id)
    order_id: str = fee.order_id
    existing_order: Order = await order_crud.get_one(order_id)
    deleted_fee: Fee = await fee_crud.delete_one(user.app_metadata.get("account_id"), fee_id)
    await order_fee_balance_controller.handle_order_fee_drop_off(fee_id, existing_order.account_id)
    sum_of_fees: Decimal = deleted_fee.fee_amount
    is_adding: bool = False
    feeType: FeeType = await FeeType.filter(id=deleted_fee.type.id).first()

    new_fee_tax: Decimal = 0

    if account.cms_attributes.get("charge_tax", True):
        if feeType.is_taxable:
            new_fee_tax = await balance_controller.handle_order_tax_calc(existing_order, sum_of_fees, is_adding)
    total_rb_change: Decimal = sum_of_fees + new_fee_tax

    await balance_controller.order_balance_adjustment(existing_order, total_rb_change, is_adding)

    return Status(message="Fee deleted")

@atomic()
async def delete_rush_fee(order_id: str, user: Auth0User, account: Account) -> Status:
    existing_order: Order = await order_crud.get_one(order_id)
    deleted_fee: Fee = await fee_crud.remove_order_rush_fees(order_id, user.app_metadata.get("account_id"))
    # order_id: str = deleted_fee.order_id
    # grab sum of fees
    sum_of_fees: Decimal = sum([fee.fee_amount for fee in deleted_fee])
    await order_fee_balance_controller.handle_order_fee_drop_off(deleted_fee[0].id, existing_order.account_id)

    is_adding: bool = False
    feeType: FeeType = await FeeType.filter(id=deleted_fee[0].type_id).first()

    new_fee_tax: Decimal = 0
    if account.cms_attributes.get("charge_tax", True):
        if feeType.is_taxable:
            new_fee_tax = await balance_controller.handle_order_tax_calc(existing_order, sum_of_fees, is_adding)
    total_rb_change: Decimal = sum_of_fees + new_fee_tax
    await note_crud.create(
        NoteInSchema(
            title="Rush Fee Removed",
            content="Rush Fee was removed",
            author_id=user.app_metadata.get("id"),
            order_id=order_id,
        )
    )

    await balance_controller.order_balance_adjustment(existing_order, total_rb_change, is_adding)

    return Status(message="Fee deleted")
