# Python imports
# import logging
# import os
# import random
# Python imports
from decimal import ROUND_HALF_UP, Decimal
from typing import List

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import order_fee_balance as order_fee_balance_controller
from src.crud.fee_crud import fee_crud
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.database.models.account import Account
from src.database.models.fee import Fee
from src.database.models.orders.order import Order
from src.schemas.order_fee_balance import OrderFeeBalanceIn, OrderFeeBalanceOut


# from fastapi import HTTPException, status
# from tortoise import Model
# from tortoise.exceptions import DoesNotExist


async def create_order_fee_balance(order_fee_balance: OrderFeeBalanceIn, user: Auth0User = None) -> OrderFeeBalanceOut:
    saved_order_fee_balance = await order_fee_balance_crud.create(order_fee_balance)
    return saved_order_fee_balance


async def handle_initial_fee_balance(fees: List[OrderFeeBalanceIn]) -> None:
    """
    Create the initial fee balance on this order using the calculated bank fees for now if it exists or set to zero if there is no remaining balance
    """
    await order_fee_balance_crud.bulk_create(fees, len(fees))


async def handle_order_fee_drop_off(fee_id: str, account_id: int):
    await order_fee_balance_crud.drop_balances(fee_id, account_id)


async def handle_add_order_fee_balance(order: Order, fee: Fee, added_balance: Decimal, is_adding):
    current_fee_balance = await order_fee_balance_crud.get_latest_balance(order.account_id, fee.id, order.id)
    if current_fee_balance:
        new_balance = added_balance + current_fee_balance.remaining_balance
        if not is_adding:
            new_balance = current_fee_balance.remaining_balance - added_balance
        if new_balance < 0:
            new_balance = 0
        create_order_fee_balance: OrderFeeBalanceIn = OrderFeeBalanceIn(
            remaining_balance=new_balance,
            order_id=current_fee_balance.order_id,
            fee_id=current_fee_balance.fee_id,
            account_id=current_fee_balance.account_id,
        )
        create_order_fee_balance: OrderFeeBalanceOut = await order_fee_balance_crud.create(create_order_fee_balance)


async def handle_pay_order_fee_balance_only_fees(
    existing_order: Order, payment_amount: Decimal, transaction_type_id: str = None, order_credit_card_id: str = None
):
    fees = existing_order.fees
    update_fees_list: List[OrderFeeBalanceIn] = []
    amount_left_for_fees = payment_amount
    # sort to pay out taxable fees first
    sorted_fees = sorted(fees, key=lambda fee: (fee.calculated_is_taxable, fee.calculated_remaining_balance))
    for fee in sorted_fees:
        if payment_amount > Decimal(0):
            if fee.calculated_remaining_balance > Decimal(0):
                amount_paid = Decimal(0)
                amount_to_pay = fee.calculated_remaining_balance
                if amount_left_for_fees >= amount_to_pay:
                    # we will be paying all fees plus tax
                    amount_paid = fee.calculated_remaining_balance
                    amount_left_for_fees -= amount_paid
                else:
                    amount_paid = amount_left_for_fees
                    amount_left_for_fees -= amount_paid

                    # Append to updated fees list to create new order balances
                update_fees_list.append(
                    OrderFeeBalanceIn(
                        remaining_balance=fee.calculated_remaining_balance - amount_paid,
                        order_id=existing_order.id,
                        account_id=existing_order.account_id,
                        fee_id=fee.id,
                        transaction_type_id=transaction_type_id,
                        order_credit_card_id=order_credit_card_id,
                    )
                )

    # bulk create
    if len(update_fees_list) > 0:
        await order_fee_balance_crud.bulk_create(update_fees_list, len(update_fees_list))


async def handle_pay_order_fee_balance(
    order: Order,
    payment_amount: Decimal,
    transaction_type_id: str = None,
    order_credit_card_id: str = None,
    remaining_tax_balance: Decimal = None,
):
    """
    Retrieve all order fees and pay them down individually
    """
    total_fee_paid = Decimal(0)
    fees = order.fees
    amount_left_for_fees = payment_amount
    update_fees_list: List[OrderFeeBalanceIn] = []
    tax_to_pay = Decimal(0)
    # sort to pay out taxable fees first
    sorted_fees = sorted(fees, key=lambda fee: (fee.calculated_is_taxable, fee.calculated_remaining_balance))
    for fee in sorted_fees:
        is_taxable = fee.calculated_is_taxable
        if amount_left_for_fees > Decimal(0):
            amount_to_pay = fee.calculated_remaining_balance
            tax_on_fee = Decimal(0)
            tax_rate = order.calculated_order_tax_rate
            calculated_tax_owed = Decimal(0)
            if is_taxable:
                is_taxable = True
                # This is a taxable fee add tax to amount to pay
                calculated_tax_owed = fee.calculated_remaining_balance * tax_rate
                amount_to_pay += calculated_tax_owed

            amount_paid = Decimal(0)

            if fee.calculated_remaining_balance > Decimal(0):

                if amount_left_for_fees >= amount_to_pay:
                    # we will be paying all fees plus tax
                    amount_paid = fee.calculated_remaining_balance
                    tax_component = calculated_tax_owed
                    if tax_component > remaining_tax_balance:
                        tax_component = remaining_tax_balance
                    tax_to_pay += tax_component
                    amount_left_for_fees -= amount_paid + tax_component
                else:
                    # Funds left for fee payment is less than the fee total plus tax so paying off what can be paid
                    if is_taxable:
                        tax_component = amount_left_for_fees / (1 + tax_rate) * tax_rate
                        tax_to_pay += tax_component
                        if tax_component > remaining_tax_balance:
                            tax_component = remaining_tax_balance
                        amount_paid = amount_left_for_fees - tax_component
                        amount_left_for_fees -= amount_paid + tax_component
                    else:
                        # Not taxed so everything is for fee
                        amount_paid = amount_left_for_fees
                        amount_left_for_fees -= amount_paid

            total_fee_paid += amount_paid
                # Append to updated fees list to create new order balances
            update_fees_list.append(
                OrderFeeBalanceIn(
                    remaining_balance=fee.calculated_remaining_balance - amount_paid,
                    order_id=order.id,
                    account_id=order.account_id,
                    fee_id=fee.id,
                    transaction_type_id=transaction_type_id,
                    order_credit_card_id=order_credit_card_id,
                )
            )
        else:
            break
    # bulk create
    if len(update_fees_list) > 0:
        await order_fee_balance_crud.bulk_create(update_fees_list, len(update_fees_list))
    return tax_to_pay, total_fee_paid
