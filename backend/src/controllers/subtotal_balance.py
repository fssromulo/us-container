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
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.database.models.orders.order import Order
from src.schemas.subtotal_balance import SubtotalBalanceIn, SubtotalBalanceOut


async def create_subtotal_balance(tax_balance: SubtotalBalanceIn) -> SubtotalBalanceOut:
    saved_tax_balance = await subtotal_balance_crud.create(tax_balance)
    return saved_tax_balance


async def handle_order_subtotal_balance_update(
    order_id: str,
    current_balance: Decimal,
    amt_to_alter: Decimal,
    is_adding: bool = True,
    transaction_type_id=None,
    order_credit_card_id=None,
) -> None:

    new_balance = current_balance + amt_to_alter if is_adding else current_balance - amt_to_alter

    create_obj: SubtotalBalanceIn = SubtotalBalanceIn(
        balance=new_balance,
        order_id=order_id,
        transaction_type_id=transaction_type_id,
        order_credit_card_id=order_credit_card_id,
    )

    await subtotal_balance_crud.create(create_obj)


async def handle_subtotal_balance_paydown(
    existing_order: Order, amt_to_alter: Decimal, is_adding: bool, transaction_type_id=None, order_credit_card_id=None
) -> None:
    current_rent_period_fee_bal: Decimal = existing_order.calculated_order_subtotal_balance
    current_balance: Decimal = current_rent_period_fee_bal

    await handle_order_subtotal_balance_update(
        existing_order.id, current_balance, amt_to_alter, is_adding, transaction_type_id, order_credit_card_id
    )
