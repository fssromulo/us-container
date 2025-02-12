# Python imports
# import logging
# import os
# import random

# Pip imports
# from fastapi import HTTPException, status
# from tortoise import Model
# from tortoise.exceptions import DoesNotExist

# Python imports
from decimal import Decimal

# Internal imports
from src.auth.auth import Auth0User
from src.crud.tax_balance_crud import tax_balance_crud
from src.database.models.orders.order import Order
from src.schemas.tax_balance import TaxBalanceIn, TaxBalanceOut


async def create_tax_balance(tax_balance: TaxBalanceIn) -> TaxBalanceOut:
    saved_tax_balance = await tax_balance_crud.create(tax_balance)
    return saved_tax_balance


async def handle_order_tax_balance_update(
    order_id: str,
    current_balance: Decimal,
    amt_to_alter: Decimal,
    is_adding: bool = True,
    transaction_type_id=None,
    order_credit_card_id=None,
) -> None:

    new_balance = current_balance + amt_to_alter if is_adding else current_balance - amt_to_alter

    create_obj: TaxBalanceIn = TaxBalanceIn(
        balance=new_balance,
        order_id=order_id,
        tax_rate=0,
        transaction_type_id=transaction_type_id,
        order_credit_card_id=order_credit_card_id,
    )

    await tax_balance_crud.create(create_obj)


async def handle_tax_balance_paydown(
    existing_order: Order, amt_to_alter: Decimal, is_adding: bool, transaction_type_id=None, order_credit_card_id=None
) -> None:
    current_rent_period_fee_bal: Decimal = existing_order.calculated_order_tax_balance
    current_balance: Decimal = current_rent_period_fee_bal

    await handle_order_tax_balance_update(
        existing_order.id, current_balance, amt_to_alter, is_adding, transaction_type_id, order_credit_card_id
    )
