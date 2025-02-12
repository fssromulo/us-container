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
from src.crud.rent_period_total_balance_crud import rent_period_total_balance_crud
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn, RentPeriodTotalBalanceOut


async def create_rent_period_total_balance(
    rent_period_total_balance: RentPeriodTotalBalanceIn,
) -> RentPeriodTotalBalanceOut:
    saved_rent_period_total_balance = await rent_period_total_balance_crud.create(rent_period_total_balance)
    return saved_rent_period_total_balance


async def handle_rent_period_total_balance_update(
    rent_period_id: str, current_balance: Decimal, amt_to_alter: Decimal, is_adding: bool = True
):
    """
    Handles the update of the total balance for a specific rent period.

    Args:
        rent_period_id (str): The unique identifier of the rent period.
        current_balance (Decimal): The current total balance for the rent period.
        amt_to_alter (Decimal): The amount to be added or subtracted from the current total balance.
        is_adding (bool, optional): A flag indicating whether to add or subtract the amount from the current balance.
                                    Defaults to True (addition).

    Returns:
        None

    Raises:
        Any exceptions raised during the operation will be propagated.

    Example:
        # Update the total balance by subtracting $75.50
        await handle_rent_period_total_balance_update("12345", Decimal("1000.00"), Decimal("75.50"), is_adding=False)
    """

    # Calculate the new total balance based on whether we're adding or subtracting
    new_balance = current_balance + amt_to_alter if is_adding else current_balance - amt_to_alter

    # Create a RentPeriodTotalBalanceIn object to store the updated remaining total balance
    create_obj: RentPeriodTotalBalanceIn = RentPeriodTotalBalanceIn(
        remaining_balance=new_balance, rent_period_id=rent_period_id
    )

    # Persist the updated total balance to the database
    await rent_period_total_balance_crud.create(create_obj)
