# Python imports

# Pip imports

# Python imports
from decimal import Decimal
from typing import List, Type
from tortoise.transactions import atomic

# Pip imports
from tortoise.models import Model

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import balance as balance_controller
from src.crud.rent_period_crud import rent_period_crud
from src.crud.rent_period_fee_crud import rent_period_fee_crud
from src.database.models.fee_type import FeeType
from src.database.models.rent_period import RentPeriod
from src.database.models.rent_period_fee import RentPeriodFee
from src.schemas.rent_period_fee import RentPeriodFeeIn, UpdateRentPeriodFee
from src.schemas.token import Status
from src.crud.rent_period_tax_balance_crud import RentPeriodTaxBalanceIn, rent_period_tax_balance_crud

@atomic()
async def create_rent_period_fees(rent_period_fees: List[RentPeriodFeeIn]) -> List[RentPeriodFeeIn]:
    db_model: Type[Model] = rent_period_fee_crud.db_model
    created_rent_period_fees: List[RentPeriodFee] = await db_model.bulk_create(
        [db_model(**rpf.dict()) for rpf in rent_period_fees]
    )
    rent_period_id: str = rent_period_fees[0].rent_period_id
    existing_rent_period: RentPeriod = await rent_period_crud.get_one(rent_period_id)
    feeTypes: List[FeeType] = await FeeType.filter(
        id__in=[currentFee.type_id for currentFee in created_rent_period_fees]
    )

    sum_of_fees: Decimal = sum(rent_period_fee.fee_amount for rent_period_fee in created_rent_period_fees)
    fee_to_be_taxed: Decimal = 0
    new_fee_tax: Decimal = 0

    for f in feeTypes:
        if f.is_taxable:
            for g in created_rent_period_fees:
                if g.type_id == f.id:
                    fee_to_be_taxed += g.fee_amount

    if fee_to_be_taxed != 0:
        new_fee_tax = await balance_controller.handle_rent_period_tax_calc(existing_rent_period, fee_to_be_taxed, True)

    total_amount_change: Decimal = sum_of_fees + new_fee_tax

    try:
        await balance_controller.rent_period_fee_balance_adjustment(
            existing_rent_period, sum_of_fees, total_amount_change
        )
        
    except Exception as e:
        raise e
    
    #tax balance calculation
    current_rent_period_tax_bal: Decimal = existing_rent_period.calculated_rent_period_tax_balance
    new_balance = current_rent_period_tax_bal + new_fee_tax

    create_obj: RentPeriodTaxBalanceIn = RentPeriodTaxBalanceIn(
        balance=new_balance,
        rent_period_id=existing_rent_period.id,
        tax_rate=0,
        transaction_type_id=None,
        order_credit_card_id=None,
    )

    await rent_period_tax_balance_crud.create(create_obj)

    return created_rent_period_fees

@atomic()
async def update_rent_period_fee(rent_period_fees: List[UpdateRentPeriodFee]) -> Status:
    update_rent_period_fees_list: List[RentPeriodFee] = []
    rent_period_fees_change_amount: Decimal = 0
    rent_period_id: str = rent_period_fees[0].rent_period_id
    existing_rent_period: RentPeriod = await rent_period_crud.get_one(rent_period_id)

    for f in rent_period_fees:
        copy_fee = f.copy()
        rent_period_fees_change_amount += Decimal(copy_fee.rent_period_fee_balance_change)
        del copy_fee.rent_period_fee_balance_change
        new_rent_period_fee: RentPeriodFee = RentPeriodFee(**copy_fee.dict())
        new_rent_period_fee.fee_type = copy_fee.fee_type
        update_rent_period_fees_list.append(new_rent_period_fee)
    await RentPeriodFee.bulk_update(update_rent_period_fees_list, fields=["fee_type", "fee_amount", "type_id"])

    feeTypes: List[FeeType] = await FeeType.filter(id__in=[currentFee.type_id for currentFee in rent_period_fees])
    taxable_fees_total: Decimal = 0
    fee_tax_change: Decimal = 0
    if rent_period_fees_change_amount != 0:
        is_adding: bool = rent_period_fees_change_amount > 0
        for f in feeTypes:
            if f.is_taxable:
                for g in rent_period_fees:
                    if g.type_id == str(f.id):
                        taxable_fees_total += g.rent_period_fee_balance_change

        if taxable_fees_total != 0:
            fee_tax_change = await balance_controller.handle_rent_period_tax_calc(
                existing_rent_period, taxable_fees_total, is_adding
            )

        fees_with_tax: Decimal = rent_period_fees_change_amount + fee_tax_change
        try:
            await balance_controller.rent_period_fee_balance_adjustment(
                existing_rent_period, rent_period_fees_change_amount, fees_with_tax, is_adding
            )
        except Exception as e:
            raise e
        
    #tax balance calculation
    current_rent_period_tax_bal: Decimal = existing_rent_period.calculated_rent_period_tax_balance
    new_balance = current_rent_period_tax_bal + fee_tax_change if is_adding else current_rent_period_tax_bal - fee_tax_change

    create_obj: RentPeriodTaxBalanceIn = RentPeriodTaxBalanceIn(
        balance=new_balance,
        rent_period_id=existing_rent_period.id,
        tax_rate=0,
        transaction_type_id=None,
        order_credit_card_id=None,
    )

    await rent_period_tax_balance_crud.create(create_obj)
    return Status(message="Rent Period Fee updated")

@atomic()
async def delete_rent_period_fee(rent_period_fee_id: str, user: Auth0User) -> Status:
    deleted_rent_period_fee: RentPeriodFee = await rent_period_fee_crud.delete_one(
        user.app_metadata.get("account_id"), rent_period_fee_id
    )
    rent_period_id: str = deleted_rent_period_fee.rent_period_id
    existing_rent_period: RentPeriod = await rent_period_crud.get_one(rent_period_id)
    sum_of_fees: Decimal = deleted_rent_period_fee.fee_amount
    is_adding: bool = False
    feeType: FeeType = await FeeType.filter(id=deleted_rent_period_fee.type_id).first()

    new_fee_tax: Decimal = 0
    if feeType.is_taxable:
        new_fee_tax = await balance_controller.handle_rent_period_tax_calc(existing_rent_period, sum_of_fees, is_adding)
    total_rb_change: Decimal = sum_of_fees + new_fee_tax

    try:
        await balance_controller.rent_period_fee_balance_adjustment(
            existing_rent_period, sum_of_fees, total_rb_change, is_adding
        )

        
    except Exception as e:
        raise e
    
    #tax balance calculation
    current_rent_period_tax_bal: Decimal = existing_rent_period.calculated_rent_period_tax_balance
    new_balance = current_rent_period_tax_bal - new_fee_tax

    create_obj: RentPeriodTaxBalanceIn = RentPeriodTaxBalanceIn(
        balance=new_balance,
        rent_period_id=existing_rent_period.id,
        tax_rate=0,
        transaction_type_id=None,
        order_credit_card_id=None,
    )

    await rent_period_tax_balance_crud.create(create_obj)

    return Status(message="Rent Period Fee deleted")