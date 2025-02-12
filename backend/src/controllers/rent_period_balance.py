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
from src.crud.rent_period_balance_crud import rent_period_balance_crud
from src.schemas.rent_period_balance import RentPeriodBalanceIn, RentPeriodBalanceOut


async def create_rent_period_balance(rent_period_balance: RentPeriodBalanceIn) -> RentPeriodBalanceOut:
    saved_rent_period_balance = await rent_period_balance_crud.create(rent_period_balance)
    return saved_rent_period_balance


async def handle_rent_period_balance_update(
    rent_period_id: str,
    current_balance: Decimal,
    amt_to_alter: Decimal,
    is_adding: bool = True,
    transaction_type_uuid: str = None,
    order_credit_card_object_id: str = None,
):
    """
    Handles the update of the balance for a specific rent period.

    Args:
        rent_period_id (str): The unique identifier of the rent period.
        current_balance (Decimal): The current balance for the rent period.
        amt_to_alter (Decimal): The amount to be added or subtracted from the current balance.
        is_adding (bool, optional): A flag indicating whether to add or subtract the amount from the current balance.
                                    Defaults to True (addition).

    Returns:
        None

    Raises:
        Any exceptions raised during the operation will be propagated.

    Example:
        # Update the balance by adding $100.50
        await handle_rent_period_balance_update("12345", Decimal("500.75"), Decimal("100.50"), is_adding=True)
    """

    # Calculate the new balance based on whether we're adding or subtracting
    new_balance = current_balance + amt_to_alter if is_adding else current_balance - amt_to_alter

    if new_balance < 0:
        raise Exception("Rent period balance less than 0 on paydown")

    # Create a RentPeriodBalanceIn object to store the updated remaining balance
    create_obj: RentPeriodBalanceIn = RentPeriodBalanceIn(
        remaining_balance=new_balance,
        rent_period_id=rent_period_id,
        transaction_type_id=transaction_type_uuid,
        order_credit_card_id=order_credit_card_object_id,
    )

    # Persist the updated balance to the database
    await rent_period_balance_crud.create(create_obj)
