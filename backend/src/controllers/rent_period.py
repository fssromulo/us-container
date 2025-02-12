# Python imports
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Union

# Pip imports
from loguru import logger
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import fee_type as fee_type_controller
from src.controllers import orders as order_controller
from src.controllers import rent_period as rent_period_controller
from src.controllers import rent_period_balance as rent_period_balance_controller
from src.controllers import rent_period_fee as rent_period_fee_controller
from src.controllers import rent_period_fee_balance as rent_period_fee_balance_controller
from src.controllers import rent_period_tax as rent_period_tax_controller
from src.controllers import rent_period_total_balance as rent_period_total_balance_controller
from src.crud.rent_period_crud import rent_period_crud
from src.crud.rent_period_tax_balance_crud import rent_period_tax_balance_crud
from src.crud.tax_crud import tax_crud
from src.crud.order_crud import order_crud, OrderIn
from src.crud.account_crud import account_crud
from src.crud.rent_period_tax_crud import rent_period_tax_crud
from src.crud.rent_period_tax_balance_crud import rent_period_tax_balance_crud
from src.crud.rent_period_fee_balance_crud import rent_period_fee_balance_crud
from src.crud.rent_period_balance_crud import rent_period_balance_crud
from src.crud.rent_period_total_balance_crud import rent_period_total_balance_crud
from src.crud.rent_period_fee_crud import rent_period_fee_crud
from src.crud.transaction_type_crud import transaction_type_crud
from src.database.models.fee_type import FeeType
from src.database.models.orders.order import Order
from src.database.models.rent_period import RentPeriod
from src.database.models.rent_period_balance import RentPeriodBalance
from src.database.models.rent_period_fee import RentPeriodFee
from src.database.models.rent_period_fee_balance import RentPeriodFeeBalance
from src.database.models.rent_period_tax import RentPeriodTax
from src.database.models.rent_period_total_balance import RentPeriodTotalBalance
from src.schemas.payment import OtherPayment, Payment
from src.schemas.rent_period import RentPeriodIn
from src.schemas.rent_period_balance import RentPeriodBalanceIn
from src.schemas.rent_period_fee import RentPeriodFeeIn
from src.schemas.rent_period_fee_balance import RentPeriodFeeBalanceIn
from src.schemas.rent_period_info import UpdatedPeriod
from src.schemas.rent_period_tax import RentPeriodTaxIn
from src.schemas.rent_period_tax_balance import RentPeriodTaxBalanceIn
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn
from src.schemas.transaction_type import TransactionTypeIn, TransactionType
from src.utils.convert_time import convert_time_date


# import logging
# import os
# import random

# from fastapi import HTTPException, status
# from tortoise import Model
# from tortoise.exceptions import DoesNotExist


@atomic()
async def delete_rent_period(rent_period_id, user):
    rent_period = await rent_period_crud.get_one(rent_period_id)

    for tax in rent_period.rent_period_taxes:
        await rent_period_tax_crud.delete_one(user.app_metadata['account_id'], tax.id)

    for tax_balance in rent_period.rent_period_tax_balance:
        await rent_period_tax_balance_crud.delete_one(user.app_metadata['account_id'], tax_balance.id)

    for fee_balance in rent_period.rent_period_fee_balances:
        await rent_period_fee_balance_crud.delete_one(user.app_metadata['account_id'], fee_balance.id)

    for balance in rent_period.rent_period_balances:
        await rent_period_balance_crud.delete_one(user.app_metadata['account_id'], balance.id)

    for total_balance in rent_period.rent_period_total_balances:
        await rent_period_total_balance_crud.delete_one(user.app_metadata['account_id'], total_balance.id)

    for fee in rent_period.rent_period_fees:
        await rent_period_fee_crud.delete_one(user.app_metadata['account_id'], fee.id)

    for tt in rent_period.transaction_type_rent_period:
        await transaction_type_crud.update(
            user.app_metadata['account_id'],
            tt.id,
            TransactionType(account_id=user.app_metadata['account_id'], rent_period_id=None),
        )

    await rent_period_crud.delete_one(rent_period_id)


async def create_rent_period(rent_period: RentPeriodIn) -> RentPeriod:
    saved_rent_period: RentPeriod = await rent_period_crud.create(rent_period)
    return saved_rent_period


async def update_rent_period(rent_period_in: RentPeriodIn, rent_period_id: str) -> RentPeriod:
    saved_rent_period: RentPeriod = await rent_period_crud.update(rent_period_id, rent_period_in)
    return saved_rent_period


def get_contract_start_date(account) -> datetime:
    daysToAdd: int = 0
    currentDate = datetime.today()
    daysToAdd: int = account.cms_attributes.get('rent_options', {}).get('contract_delivery_days', 0)

    if daysToAdd == 0:
        return None

    updatedDate = currentDate + timedelta(days=daysToAdd)
    return updatedDate


async def calculate_rent_period_tax(
    order: Order, account_id: int, rent_fee_balance_amount: Decimal, rent_balance_amount: Decimal
) -> Decimal:
    """
    Calculate the tax for a rent period based on fee balance and rent balance.

    Args:
        order (Order): The order associated with the rent period.
        account_id (int): The account ID.
        rent_fee_balance_amount (Decimal): The fee balance amount.
        rent_balance_amount (Decimal): The rent balance amount.

    Returns:
        Decimal: The calculated tax amount.
    """
    tax_state = (
        order.address.state if order.address else order.single_customer.customer_contacts[0].customer_address.state
    )

    tax_rate = await tax_crud.get_tax_rate(account_id, tax_state)
    tax_amount = (Decimal(rent_fee_balance_amount) + Decimal(rent_balance_amount)) * Decimal(tax_rate or 0)
    tax = tax_amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    return tax


async def get_rent_period(rent_period_id: str) -> RentPeriod:
    """
    Retrieve a rent period by ID.

    Args:
        rent_period_id (str): The ID of the rent period.

    Returns:
        RentPeriodOut: The rent period information.
    """
    rent_period: RentPeriod = await rent_period_crud.get_one(rent_period_id)
    return rent_period


async def handle_create_rent_period(
    amount_owed: Decimal,
    order_id: str,
    is_initial_rent_period: bool,
    start_date: datetime = None,
    end_date: datetime = None,
) -> str:
    """
    Handle the creation of a new rent period.

    Args:
        amount_owed (Decimal): The amount owed for the rent period.
        order_id (str): The ID of the associated order.

    Returns:
        str: The ID of the created rent period.
    """
    # TODO redo this annotation
    # TODO make sure that the start date gets inputed properly
    create_rent_period: RentPeriodIn
    if is_initial_rent_period:
        create_rent_period = RentPeriodIn(amount_owed=amount_owed, order_id=order_id)
    else:
        create_rent_period = RentPeriodIn(
            amount_owed=amount_owed, order_id=order_id, start_date=start_date, end_date=end_date
        )

    saved_rent_period: RentPeriod = await rent_period_controller.create_rent_period(create_rent_period)
    rent_period_id = saved_rent_period.id
    return rent_period_id


async def handle_create_rent_period_fee(
    down_payment_amount: Decimal,
    down_payment_strategy: str,
    rent_period_id: str,
    account_id: int,
    quick_rent: bool,
    pickup: Decimal,
    drop_off: Decimal,
) -> RentPeriodFee:
    """
    Handle the creation of a rent period fee.

    Args:
        down_payment_amount (Decimal): The fee amount.
        down_payment_strategy (str): The fee description.
        rent_period_id (str): The ID of the associated rent period.
        account_id (int): The ID of the current user's account

    Returns:
        RentPeriodFee: The created rent period fee.
    """

    if down_payment_strategy == 'FIRST_MONTH_PLUS_DELIVERY_&_PICKUP':
        drop_off_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "DROP_OFF")

        create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
            fee_amount=down_payment_amount / 2 if not quick_rent else drop_off,
            type_id=drop_off_fee_type.id,
            description=down_payment_strategy,
            rent_period_id=rent_period_id,
        )
        saved_rent_period_fees_drop_off: List[RentPeriodFee] = await rent_period_fee_controller.create_rent_period_fees(
            [create_rent_period_fee]
        )

        pick_up_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "PICK_UP")

        create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
            fee_amount=down_payment_amount / 2 if not quick_rent else pickup,
            type_id=pick_up_fee_type.id,
            description=down_payment_strategy,
            rent_period_id=rent_period_id,
        )
        saved_rent_period_fees_pick_up: List[RentPeriodFee] = await rent_period_fee_controller.create_rent_period_fees(
            [create_rent_period_fee]
        )

        return saved_rent_period_fees_drop_off[0], saved_rent_period_fees_pick_up[0]
    elif down_payment_strategy == 'FIRST_MONTH_PLUS_DELIVERY':
        drop_off_fee_type: FeeType = await fee_type_controller.fetch_fee_type_by_name(account_id, "DROP_OFF")

        create_rent_period_fee: RentPeriodFeeIn = RentPeriodFeeIn(
            fee_amount=down_payment_amount if not quick_rent else drop_off,
            type_id=drop_off_fee_type.id,
            description=down_payment_strategy,
            rent_period_id=rent_period_id,
        )
        saved_rent_period_fees_drop_off: List[RentPeriodFee] = await rent_period_fee_controller.create_rent_period_fees(
            [create_rent_period_fee]
        )

        return saved_rent_period_fees_drop_off[0], None
    return None, None


async def handle_create_rent_period_fee_balance(
    saved_rent_period_fee: RentPeriodFee, rent_period_id: str
) -> RentPeriodFeeBalance:
    """
    Handle the creation of a rent period fee balance.

    Args:
        saved_rent_period_fee (RentPeriodFee): The saved rent period fee.
        rent_period_id (str): The ID of the associated rent period.

    Returns:
        RentPeriodFeeBalance: The created rent period fee balance.
    """
    create_rent_period_fee_balance: RentPeriodFeeBalanceIn = RentPeriodFeeBalanceIn(
        remaining_balance=saved_rent_period_fee.fee_amount, rent_period_id=rent_period_id
    )
    saved_rent_period_fee_balance = await rent_period_fee_balance_controller.create_rent_period_fee_balance(
        create_rent_period_fee_balance
    )
    return saved_rent_period_fee_balance


async def handle_first_payment(
    rent_options: dict, order: Order, rent_period_id: str, quick_rent: bool, drop_off=0, pickup=0
) -> RentPeriodFeeBalance:
    """
    Handle the down payment for a rent period.

    Args:
        rent_options (dict): Rental options.
        order (Order): The associated order.
        rent_period_id (str): The ID of the rent period.

    Returns:
        RentPeriodFeeBalance: The balance information after the down payment.
    """
    down_payment_strategy: Union[str, None] = rent_options.get("down_payment_strategy", "")
    down_payment_amount: Decimal = 0

    first_payment_strategy = order.first_payment_strategy
    if not first_payment_strategy:
        first_payment_strategy = down_payment_strategy

    if not quick_rent:
        if first_payment_strategy.upper() == "FIRST_MONTH_PLUS_DELIVERY_&_PICKUP":
            down_payment_amount = order.calculated_shipping_revenue_total * 2
        else:
            down_payment_amount = order.calculated_shipping_revenue_total

        if first_payment_strategy.upper() == "FIRST_MONTH_PLUS_DELIVERY":
            down_payment_amount = order.calculated_shipping_revenue_total
    else:
        down_payment_amount = order.calculated_shipping_revenue_total

    saved_rent_period_fee_drop_off, saved_rent_period_fee_pick_up = await handle_create_rent_period_fee(
        down_payment_amount,
        down_payment_strategy,
        rent_period_id,
        order.account_id,
        quick_rent=quick_rent,
        drop_off=drop_off,
        pickup=pickup,
    )

    balances = []
    if saved_rent_period_fee_drop_off and saved_rent_period_fee_pick_up:
        saved_rent_period_fee_drop_off.fee_amount += saved_rent_period_fee_pick_up.fee_amount
        saved_rent_period_fee_balance: RentPeriodFeeBalance = await handle_create_rent_period_fee_balance(
            saved_rent_period_fee_drop_off, rent_period_id
        )
        balances.append(saved_rent_period_fee_balance)
    elif saved_rent_period_fee_drop_off:
        saved_rent_period_fee_balance: RentPeriodFeeBalance = await handle_create_rent_period_fee_balance(
            saved_rent_period_fee_drop_off, rent_period_id
        )
        balances.append(saved_rent_period_fee_balance)
    return balances


async def handle_create_rent_period_balance(amount_owed: Decimal, rent_period_id: str) -> RentPeriodBalance:
    """
    Handle the creation of a rent period balance.

    Args:
        amount_owed (Decimal): The amount owed for the rent period.
        rent_period_id (str): The ID of the associated rent period.

    Returns:
        RentPeriodBalance: The created rent period balance.
    """
    create_rent_period_balance: RentPeriodBalanceIn = RentPeriodBalanceIn(
        remaining_balance=amount_owed, rent_period_id=rent_period_id
    )
    saved_rent_period_balance: RentPeriodBalance = await rent_period_balance_controller.create_rent_period_balance(
        create_rent_period_balance
    )
    return saved_rent_period_balance


async def handle_create_rent_period_tax(rent_period_tax: Decimal, rent_period_id: str) -> RentPeriodTax:
    """
    Handle the creation of a rent period tax.

    Args:
        rent_period_tax (Decimal): The tax amount for the rent period.
        rent_period_id (str): The ID of the associated rent period.

    Returns:
        RentPeriodTax: The created rent period tax information.
    """
    create_rent_period_tax: RentPeriodTaxIn = RentPeriodTaxIn(tax_amount=rent_period_tax, rent_period_id=rent_period_id)
    saved_rent_tax: RentPeriodTax = await rent_period_tax_controller.create_rent_period_tax(create_rent_period_tax)
    await rent_period_tax_balance_crud.create(
        RentPeriodTaxBalanceIn(balance=rent_period_tax, rent_period_id=rent_period_id, tax_rate=0)
    )
    return saved_rent_tax


async def handle_create_rent_period_total_balance(
    rent_period_total_balance: Decimal, rent_period_id: str
) -> RentPeriodTotalBalance:
    """
    Handle the creation of a rent period total balance.

    Args:
        rent_period_total_balance (Decimal): The total balance amount for the rent period.
        rent_period_id (str): The ID of the associated rent period.

    Returns:
        RentPeriodTotalBalance: The created rent period total balance information.
    """
    create_rent_period_total_balance: RentPeriodTotalBalanceIn = RentPeriodTotalBalanceIn(
        remaining_balance=rent_period_total_balance, rent_period_id=rent_period_id
    )

    saved_rent_period_total_balance: RentPeriodTotalBalance = (
        await rent_period_total_balance_controller.create_rent_period_total_balance(create_rent_period_total_balance)
    )

    return saved_rent_period_total_balance


async def generate_rent_period(
    amount_owed: Decimal,
    order: Order,
    rent_options: dict,
    is_initial_rent_period: bool = False,
    start_date: datetime = None,
    end_date: datetime = None,
    quick_rent: bool = False,
    drop_off=Decimal(0),
    pickup=Decimal(0),
) -> None:
    """
    Generate rent periods for an order.

    Args:
        amount_owed (Decimal): The amount owed for the rent period.
        order (Order): The associated order.
        rent_options (dict): Rental options.
        is_initial_rent_period (bool): Indicates if it's the initial rent period.

    Returns:
        None
    """
    # TODO redo this annotation
    rent_period_id: str

    if is_initial_rent_period:
        rent_period_id = await handle_create_rent_period(amount_owed, order.id, is_initial_rent_period)
    else:
        rent_period_id = await handle_create_rent_period(
            amount_owed, order.id, is_initial_rent_period, start_date, end_date
        )

    rent_period_tax: Decimal
    rent_period_total_balance: Decimal

    # we only want the downpayment calc to happen on the initial rent_period
    saved_rent_period_fee_balances: List[RentPeriodFeeBalance] = []
    if is_initial_rent_period:
        saved_rent_period_fee_balances = await handle_first_payment(
            rent_options, order, rent_period_id, quick_rent=quick_rent, drop_off=drop_off, pickup=pickup
        )

    saved_rent_period_balance: RentPeriodBalance = await handle_create_rent_period_balance(amount_owed, rent_period_id)

    # This could not be set when its not the inital one, so we set the default to 0
    saved_rent_period_fee_balance_amt = 0
    for balance in saved_rent_period_fee_balances:
        saved_rent_period_fee_balance_amt += balance.remaining_balance if balance else 0

    if order.tax_exempt is False:
        rent_period_tax = await calculate_rent_period_tax(
            order,
            order.account_id,
            saved_rent_period_fee_balance_amt,
            saved_rent_period_balance.remaining_balance,
        )
        saved_rent_tax: RentPeriodTax = await handle_create_rent_period_tax(rent_period_tax, rent_period_id)

        rent_options["rent_period_paid"] = (
            True if rent_options.get("rent_period_paid", None) and start_date.date() <= datetime.now().date() else False
        )

        rent_period_total_balance = (
            (
                saved_rent_period_fee_balance_amt
                + saved_rent_period_balance.remaining_balance
                + saved_rent_tax.tax_amount
            )
            if not rent_options["rent_period_paid"]
            else 0
        )
    else:
        rent_options["rent_period_paid"] = (
            True if rent_options.get("rent_period_paid", None) and start_date.date() <= datetime.now().date() else False
        )

        rent_period_total_balance = (
            (saved_rent_period_fee_balance_amt + saved_rent_period_balance.remaining_balance)
            if not rent_options["rent_period_paid"]
            else 0
        )

    await handle_create_rent_period_total_balance(rent_period_total_balance, rent_period_id)


async def handle_initial_rent_period(
    order_id: str, user: Auth0User, rent_options: dict, quick_rent=False, drop_off=0, pickup=0
) -> None:
    """
    Handle the initial rent period for an order.

    Args:
        order_id (str): The ID of the order.
        user (Auth0User): The user information.
        rent_options (dict): Rental options.

    Returns:
        None
    """
    is_initial_rent_period: bool = True
    # grabbing the fresh order
    order: Order = await order_controller.get_order_by_id(order_id, user)

    amount_owed: Decimal = order.calculated_monthly_subtotal

    await generate_rent_period(
        amount_owed,
        order,
        rent_options,
        is_initial_rent_period,
        quick_rent=quick_rent,
        drop_off=drop_off,
        pickup=pickup,
    )


def _is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _get_last_day_of_rent_period(charge_day: int, is_thirty_month: bool, is_leap_year: bool, is_february: bool):
    """Determine the last day of the rent period"""
    if charge_day != 1:
        res = charge_day - 1
        if is_february:
            if res >= 28:
                res = 29 if is_leap_year else 28
        if is_thirty_month:
            if res > 30:
                res = 30
        return res

    if is_february:
        return 29 if is_leap_year else 28
    if is_thirty_month:
        return 30
    return 31


def generate_single_rent_period_dates(
    loop_index: int, current_date: datetime, rent_due_on_day: int
) -> Tuple[datetime, datetime]:
    """
    Generate a single rent period based on the current date and the day on which rent is due.

    Args:
        loop_index (int): The loop index indicating the number of months to add to the current date.
        current_date (datetime): The current date.
        rent_due_on_day (int): The day on which rent is due.

    Returns:
        Tuple[datetime, datetime]: A tuple containing the start and end dates of the rent period. The first element
        is the start date, and the second element is the end date.
    """
    year = current_date.year + (current_date.month - 1 + loop_index) // 12
    month = (current_date.month - 1 + loop_index) % 12 + 1
    next_month: int
    if current_date.day > 1:
        next_month = (month % 12) + 1
    else:
        next_month = month % 12
        if rent_due_on_day == 1 and next_month == 0:
            # We are in december so we have to stay in current year and current month
            next_month = 12
        elif next_month == 0:
            next_month = 1
    next_year = year if next_month != 1 else year + 1
    if next_year == year + 1 and next_month - month <= 1 and next_month - month >= 0:
        next_year = year

    hour: int = 12

    is_february = month == 2
    is_thirty_month = month in [4, 6, 9, 11]
    is_leap = _is_leap_year(year)
    charge_day = rent_due_on_day

    # Adjust charge day for February and 30-day months
    if loop_index > 0:
        if month == 2 and ((is_leap and charge_day > 29) or (not is_leap and charge_day) > 28):
            month = next_month
            year = next_year
            charge_day = 1
        elif is_thirty_month and charge_day > 30:
            month = next_month
            year = next_year
            charge_day = 1
        elif charge_day == 31:
            month = next_month
            year = next_year
            charge_day = 1

    # Determine the start and end of the rent period
    start_of_rent_period = datetime(year, month, charge_day, hour)

    is_february = next_month == 2
    is_thirty_month = next_month in [4, 6, 9, 11]
    is_leap = _is_leap_year(next_year)

    last_day = _get_last_day_of_rent_period(charge_day, is_thirty_month, is_leap, is_february)
    end_of_rent_period = datetime(next_year, next_month, last_day, hour)

    return start_of_rent_period, end_of_rent_period


async def handle_rent_period_dates_update(
    rent_period: RentPeriod, order: Order, rent_due_on_day: int, override_start_date: datetime = None
):
    # TODO annotate this function
    end_date: datetime
    start_date = override_start_date if override_start_date else datetime.now()
    loop_index: int = 0
    rent_due_on_day: int = order.rent_due_on_day

    start_date, end_date = rent_period_controller.generate_single_rent_period_dates(
        loop_index, start_date, rent_due_on_day
    )

    update_rent_period: RentPeriodIn = RentPeriodIn(
        start_date=start_date, end_date=end_date, order_id=order.id, amount_owed=rent_period.amount_owed
    )

    await rent_period_controller.update_rent_period(update_rent_period, rent_period.id)


async def generate_rolling_rent_periods(
    rent_options: dict,
    inital_rent_period: RentPeriod,
    order: Order,
    autopay_day=None,
    quick_rent=False,
    drop_off=0,
    pickup=0,
    number_of_periods=0,
) -> None:
    # look at how many rolling rent periods they want and then generate rent period per one
    # this wont be called if it is not a down payment charge
    num_rolling_rent_periods: int = rent_options.get("rolling_rent_periods", 0) + number_of_periods
    is_initial_rent_period: bool = rent_options.get("is_initial_rent_period", False)
    amt_owed: Decimal = rent_options.get("amount", inital_rent_period.amount_owed)

    start_date = rent_options.get("start_date", datetime.now())
    start_range = len(order.rent_periods) - 1 if number_of_periods > 0 else 0
    if len(order.rent_periods) - 1 == 0 and number_of_periods > 0:
        start_range == 1

    for i in range(start_range, num_rolling_rent_periods):
        start_of_rent_period: datetime
        end_of_rent_period: datetime
        if i == 0:
            # we already have generated the inital period, so we want all the periods after the initial one
            # to be generated
            continue

        if autopay_day:
            start_of_rent_period, end_of_rent_period = generate_single_rent_period_dates(i, start_date, autopay_day)
        else:
            start_of_rent_period, end_of_rent_period = generate_single_rent_period_dates(
                i, start_date, order.rent_due_on_day
            )

        await generate_rent_period(
            amt_owed,
            order,
            rent_options,
            is_initial_rent_period,
            start_of_rent_period,
            end_of_rent_period,
            quick_rent=quick_rent,
            drop_off=drop_off,
            pickup=pickup,
        )
        if 'date_ended' in rent_options:
            logger.info(rent_options['date_ended'])
            if start_of_rent_period <= rent_options['date_ended'] <= end_of_rent_period:
                # break Stops generating periods after end date.
                break


async def modify_rent_period_due_dates(updated_period: UpdatedPeriod, subsequent_period_ids: list[str]):
    start_date = datetime.strptime(updated_period.date, '%m/%d/%Y')
    start_date = convert_time_date(start_date)
    await Order.filter(id=updated_period.order_id).update(rent_due_on_day=updated_period.rent_due_on_day)
    start_of_rent_period, end_of_rent_period = generate_single_rent_period_dates(
        0, start_date, updated_period.rent_due_on_day
    )
    await RentPeriod.filter(id=updated_period.id).update(start_date=start_of_rent_period, end_date=end_of_rent_period)
    counter = 1
    for current_id in subsequent_period_ids:
        start_of_rent_period, end_of_rent_period = generate_single_rent_period_dates(
            counter, start_date, updated_period.rent_due_on_day
        )
        counter += 1
        await RentPeriod.filter(id=current_id).update(end_date=end_of_rent_period, start_date=start_of_rent_period)
    return True


async def _handle_rent_period_tax_balance_paydown(
    existing_rent_period: RentPeriod,
    amt_to_alter: Decimal,
    is_adding: bool,
    transaction_type_uuid: str,
    order_credit_card_object_id: str,
) -> None:
    current_rent_period_fee_bal: Decimal = existing_rent_period.calculated_rent_period_tax_balance
    current_balance: Decimal = current_rent_period_fee_bal

    new_balance = current_balance + amt_to_alter if is_adding else current_balance - amt_to_alter
    # new balance cannot be less than 0
    if new_balance < 0:
        logger.info(f"New balance is less than 0 for rent period {existing_rent_period.id}")
        raise Exception("Tax balance less than 0 on paydown")
        # new_balance = 0

    # Create a RentPeriodFeeBalanceIn object to store the updated remaining fee balance
    create_obj: RentPeriodTaxBalanceIn = RentPeriodTaxBalanceIn(
        balance=new_balance,
        rent_period_id=existing_rent_period.id,
        tax_rate=0,
        transaction_type_id=transaction_type_uuid,
        order_credit_card_id=order_credit_card_object_id,
    )

    await rent_period_tax_balance_crud.create(create_obj)


async def _handle_rent_period_fee_balance_paydown(
    existing_rent_period: RentPeriod,
    amt_to_alter: Decimal,
    is_adding: bool,
    transaction_type_uuid: str,
    order_credit_card_object_id: str,
) -> None:
    # TODO annotate this
    current_rent_period_fee_bal: Decimal = existing_rent_period.calculated_rent_period_fee_balance
    current_balance: Decimal = current_rent_period_fee_bal

    await rent_period_fee_balance_controller.handle_rent_period_fee_balance_update(
        existing_rent_period.id,
        current_balance,
        amt_to_alter,
        is_adding,
        transaction_type_uuid,
        order_credit_card_object_id,
    )


async def _handle_rent_period_balance_paydown(
    existing_rent_period: RentPeriod,
    amt_to_alter: Decimal,
    is_adding: bool,
    transaction_type_uuid: str,
    order_credit_card_object_id: str,
) -> None:
    # TODO annotate this
    current_rent_period_bal: Decimal = existing_rent_period.calculated_rent_period_balance
    current_balance: Decimal = current_rent_period_bal

    await rent_period_balance_controller.handle_rent_period_balance_update(
        existing_rent_period.id,
        current_balance,
        amt_to_alter,
        is_adding,
        transaction_type_uuid,
        order_credit_card_object_id,
    )


async def _get_tax_rate(order: Order) -> Decimal:
    states = [line_item.product_state for line_item in order.line_items]

    state = ""
    if all(state == states[0] for state in states):
        state = states[0]
    tax_rate = await tax_crud.get_tax_rate(order.account_id, state)
    return tax_rate


def _get_past_and_current_rent_periods(order: Order) -> List[RentPeriod]:
    return sorted(
        list(
            filter(
                lambda period: period.calculated_rent_period_total_balance > Decimal(0),
                order.rent_periods,
            )
        ),
        key=lambda period: period.start_date,
    )


def _get_parsed_rent_periods(order: Order, period_ids: List[str]) -> List[RentPeriod]:
    return sorted(
        list(
            filter(
                lambda period: (
                    period.calculated_rent_period_total_balance > Decimal(0) and str(period.id) in period_ids
                ),
                order.rent_periods,
            )
        ),
        key=lambda period: period.start_date,
    )


async def _handle_partial_rent_pay_down(
    payment_request: Union[Payment, OtherPayment],
    rent_period: RentPeriod,
    is_adding: bool,
    order_credit_card_obj_id: str,
    transaction_type_id: str,
) -> Decimal:
    # TODO annotate this
    amt_to_alter_total_balance: Decimal = 0
    logger.info(
        f"In Partial Rent Pay Down: {payment_request.rent_period_paid_amt} {payment_request.rent_period_fee_paid_amt} {payment_request.rent_period_tax_paid_amt}"
    )
    if payment_request.rent_period_fee_paid_amt:
        # handle the adjustment of the rent_period_fee_balance
        condition_amount_to_alter: Decimal = min(
            payment_request.rent_period_fee_paid_amt, rent_period.calculated_rent_period_fee_balance
        )
        amt_to_alter_total_balance += condition_amount_to_alter
        await _handle_rent_period_fee_balance_paydown(
            rent_period, condition_amount_to_alter, is_adding, transaction_type_id, order_credit_card_obj_id
        )

    if payment_request.rent_period_paid_amt:
        # handle the adjustment of the rent_period_balance
        conditon_amount_to_alter: Decimal = min(
            payment_request.rent_period_paid_amt, rent_period.calculated_rent_period_balance
        )
        amt_to_alter_total_balance += conditon_amount_to_alter
        await _handle_rent_period_balance_paydown(
            rent_period, conditon_amount_to_alter, is_adding, transaction_type_id, order_credit_card_obj_id
        )

    if payment_request.rent_period_tax_paid_amt:
        # handle the adjustment of the rent_period_balance
        conditon_amount_to_alter: Decimal = min(
            payment_request.rent_period_tax_paid_amt, rent_period.calculated_rent_period_tax_balance
        )
        amt_to_alter_total_balance += conditon_amount_to_alter
        await _handle_rent_period_tax_balance_paydown(
            rent_period, conditon_amount_to_alter, is_adding, transaction_type_id, order_credit_card_obj_id
        )

    return amt_to_alter_total_balance


async def handle_rent_period_credit_card_pay(
    payment_request: Payment,
    exisiting_order: Order,
    rent_options: dict,
    is_down_payment_charge: bool = False,
    autopay_day: int = None,
    order_credit_card_obj_id: str = None,
    user=None,
    group_id: str = "",
    notes: str = "",
) -> None:
    """
    This will drop all of the balances to 0
    """
    # TODO annotate this
    rent_period_ids: str = payment_request.rent_period_ids

    # There can be multiple rent periods sent up to be paid off. These will be complete pay off though
    # But there can also just have a single one for if they are paying off partial amounts
    existing_rent_periods: List[RentPeriod] = list(
        filter(lambda period: str(period.id) in rent_period_ids, exisiting_order.rent_periods)
    )
    # existing_rent_period: RentPeriod
    # if len(existing_rent_periods) == 1:
    #     # if there is only one rent period then we can just grab that one bc it is the down payment
    #     existing_rent_period = existing_rent_periods[0]

    is_adding: bool = False
    for existing_rent_period in existing_rent_periods:

        current_rent_period_total_bal = existing_rent_period.calculated_rent_period_total_balance
        amt_to_alter_total_balance: Decimal = 0

        # if they are paying partially, then either one of these fields will be populated
        # there will always just be one on these calls bc it is editing a specific rent period
        if (
            payment_request.rent_period_fee_paid_amt
            or payment_request.rent_period_paid_amt
            or payment_request.rent_period_tax_paid_amt
        ):
            amt_to_alter_total_balance = await _handle_partial_rent_pay_down(
                payment_request, existing_rent_period, is_adding, order_credit_card_obj_id
            )

            await rent_period_total_balance_controller.handle_rent_period_total_balance_update(
                existing_rent_period.id, current_rent_period_total_bal, amt_to_alter_total_balance, is_adding
            )

        # but if they are not at all, then we will pay off the full amount for all the rent periods
        else:
            # if neither of the above are not set, then it is a full paydown of the rent period
            # handle the adjustment of both the rent_period_fee_balance and the rent_period_balance
            # by zeroing them out. and then also inserting a zero into the rent_period_total_balance
            # that way the tax will show as paid off as well.
            # will look at the total_paid
            amt_to_alter_total_balance += existing_rent_period.calculated_rent_period_total_balance

            if group_id == '':
                group_id = uuid.uuid4()

            if payment_request.transaction_created_at:
                transaction_created_at = datetime.strptime(
                    payment_request.transaction_created_at, '%Y-%m-%dT%H:%M:%S.%fZ'
                )
            else:
                transaction_created_at = datetime.now()

            transaction_type = await transaction_type_crud.create(
                TransactionTypeIn(
                    rent_period_id=existing_rent_period.id,
                    payment_type="CC",
                    amount=amt_to_alter_total_balance,
                    account_id=exisiting_order.account_id,
                    credit_card_object_id=order_credit_card_obj_id,
                    notes=str(notes),
                    group_id=group_id,
                    user_id=None if not user else user.id.replace("auth0|", ""),
                    transaction_effective_date=transaction_created_at,
                )
            )

            transaction_type_uuid = transaction_type.id

            await _full_period_paydown(existing_rent_period, transaction_type_uuid, order_credit_card_obj_id)

    if is_down_payment_charge:
        await generate_rolling_rent_periods(rent_options, existing_rent_period, exisiting_order, autopay_day)


async def pay_multiple_rent_period_balances_only(
    other_payment: OtherPayment, order: Order, order_credit_card_object, user=None
):
    if other_payment.lump_sum_amount:
        total_payment_amount: Decimal = other_payment.lump_sum_amount
        current_amount_leftover: Decimal = (
            total_payment_amount  # this will keep track of how much is left over to be applied to the next period
        )

        tax_rate = await _get_tax_rate(order)
        past_and_current_rent_periods = _get_past_and_current_rent_periods(order)

        transaction_type_group_id = str(uuid.uuid4())

        for period in past_and_current_rent_periods:
            period_total_balance: Decimal = period.calculated_rent_period_total_balance

            transaction_type_uuid = None
            order_credit_card_object_id = None

            transaction_type_uuid = await _handle_transactions(
                other_payment,
                period,
                order,
                order_credit_card_object,
                user,
                transaction_type_group_id,
                current_amount_leftover,
                period_total_balance,
            )

            amt_to_alter_bal: Decimal = 0

            if current_amount_leftover == 0:
                logger.info(f"Current amount leftover is 0 for period, only balance pay down {period.id}, breaking")
                break
            else:
                try:
                    tax_amount = 0
                    balance_response = await _rent_balances_paydown(
                        current_amount_leftover,
                        tax_rate,
                        transaction_type_uuid,
                        order_credit_card_object_id,
                        period,
                        'balance',
                        amt_to_alter_bal,
                        tax_amount,
                    )
                    current_amount_leftover = balance_response['current_amount_leftover']
                    amt_to_alter_bal = balance_response['amt_to_alter_total_bal']
                    tax_amount = balance_response['tax_amount']

                    if tax_amount > 0:
                        await _handle_rent_period_tax_balance_paydown(
                            period, tax_amount, False, transaction_type_uuid, order_credit_card_object_id
                        )

                    if period_total_balance > 0:
                        paydown_amount = min(current_amount_leftover, period_total_balance)
                        amt_to_alter_bal += paydown_amount
                        current_amount_leftover -= paydown_amount
                        logger.debug(
                            f"Paying down {paydown_amount} from period {period.id}. Remaining credits to be used: {current_amount_leftover}"
                        )

                    await rent_period_total_balance_controller.handle_rent_period_total_balance_update(
                        period.id, period_total_balance, amt_to_alter_bal, False
                    )

                except Exception as e:
                    logger.error(f"Error attempting to pay down a period balance in full, {e}")
                    raise e


async def _rent_balances_paydown(
    current_amount_leftover: Decimal,
    tax_rate: Decimal,
    transaction_type_uuid: str,
    order_credit_card_object_id: str,
    period: RentPeriod,
    balance_type: str,
    amt_to_alter_total_balance: Decimal,
    tax_amount: Decimal,
) -> Dict[str, Decimal]:
    """
    Handles the paydown of different types of balances within a rent period.

    Args:
        current_amount_leftover (Decimal): The remaining amount available for payment.
        tax_rate (Decimal): The applicable tax rate.
        transaction_type_uuid (str): The UUID of the transaction type.
        order_credit_card_object_id (str): The UUID of the associated credit card object.
        period (RentPeriod): The rent period instance.
        balance_type (str): The type of balance ('fee', 'balance', 'non_taxable_fee').
        amt_to_alter_total_balance (Decimal): The total balance to be altered.
        tax_amount (Decimal): The current tax amount.

    Returns:
        dict containing the updated balances
    """
    period_fee_balance: Decimal = period.calculated_rent_period_fee_balance
    period_balance: Decimal = period.calculated_rent_period_balance

    if current_amount_leftover == 0:
        return {
            'current_amount_leftover': current_amount_leftover,
            'amt_to_alter_total_bal': amt_to_alter_total_balance,
            'tax_amount': tax_amount,
        }

    non_taxable_rent_period_fees = [x for x in period.rent_period_fees if not x.type.is_taxable]
    non_taxable_rent_period_fees_sum = sum([x.fee_amount for x in non_taxable_rent_period_fees])

    original_balance = 0
    if balance_type == 'fee':
        original_balance = period_fee_balance - non_taxable_rent_period_fees_sum

        new_amt_to_paydown = min(original_balance * (1 + tax_rate), current_amount_leftover)
    elif balance_type == 'balance':
        original_balance = period_balance

        new_amt_to_paydown = min(original_balance * (1 + tax_rate), current_amount_leftover)
    elif balance_type == 'non_taxable_fee':
        if non_taxable_rent_period_fees_sum > 0 and period_fee_balance >= non_taxable_rent_period_fees_sum:
            original_balance = period_fee_balance - non_taxable_rent_period_fees_sum
        elif non_taxable_rent_period_fees_sum > 0 and period_fee_balance != 0:
            original_balance = period_fee_balance

        new_amt_to_paydown = min(original_balance, current_amount_leftover)

    if new_amt_to_paydown <= 0:
        return {
            'current_amount_leftover': current_amount_leftover,
            'amt_to_alter_total_bal': amt_to_alter_total_balance,
            'tax_amount': tax_amount,
        }

    if original_balance > 0 and balance_type != 'non_taxable_fee':
        tax_reduced_amount = new_amt_to_paydown / (1 + tax_rate)
        tax_amount = tax_amount + (new_amt_to_paydown - tax_reduced_amount)
    else:
        tax_reduced_amount = new_amt_to_paydown

    if balance_type == 'fee':
        await _handle_rent_period_fee_balance_paydown(
            period,
            tax_reduced_amount,
            False,
            transaction_type_uuid,
            order_credit_card_object_id,
        )
    elif balance_type == 'non_taxable_fee':
        await _handle_rent_period_fee_balance_paydown(
            period, tax_reduced_amount, False, transaction_type_uuid, order_credit_card_object_id
        )
    elif balance_type == 'balance':
        await _handle_rent_period_balance_paydown(
            period, tax_reduced_amount, False, transaction_type_uuid, order_credit_card_object_id
        )

    # we want to reduce what weve paid down by the total including the tax
    current_amount_leftover -= new_amt_to_paydown
    amt_to_alter_total_balance += new_amt_to_paydown

    return {
        'current_amount_leftover': current_amount_leftover,
        'amt_to_alter_total_bal': amt_to_alter_total_balance,
        'tax_amount': tax_amount,
    }


@atomic()
async def _full_period_paydown(period: RentPeriod, transaction_type_uuid: str, order_credit_card_object_id: str):
    try:
        rent_period_balance = period.calculated_rent_period_balance
        rent_period_fee_balance = period.calculated_rent_period_fee_balance
        rent_period_tax_balance = period.calculated_rent_period_tax_balance
        rent_period_total_balance = period.calculated_rent_period_total_balance

        is_adding = False

        await _handle_rent_period_balance_paydown(
            period, rent_period_balance, is_adding, transaction_type_uuid, order_credit_card_object_id
        )

        await _handle_rent_period_tax_balance_paydown(
            period, rent_period_tax_balance, is_adding, transaction_type_uuid, order_credit_card_object_id
        )
        await _handle_rent_period_fee_balance_paydown(
            period, rent_period_fee_balance, is_adding, transaction_type_uuid, order_credit_card_object_id
        )
        await rent_period_total_balance_controller.handle_rent_period_total_balance_update(
            period.id, rent_period_total_balance, rent_period_total_balance, is_adding
        )
    except Exception as e:
        logger.error(f'Error attempting to pay down a period balance in full, {e}')
        raise e


@atomic()
async def _handle_transactions(
    other_payment: OtherPayment,
    period: RentPeriod,
    order: Order,
    order_credit_card_object: any,
    user: Auth0User,
    transaction_type_group_id: str,
    current_amount_leftover: Decimal,
    period_total_balance: Decimal,
):
    transaction_type = None

    if other_payment.transaction_created_at:
        transaction_created_at = datetime.strptime(other_payment.transaction_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        transaction_created_at = datetime.now()

    if current_amount_leftover != 0 and current_amount_leftover >= period_total_balance:
        transaction_type = await transaction_type_crud.create(
            TransactionTypeIn(
                rent_period_id=period.id,
                payment_type=other_payment.payment_type,
                amount=period_total_balance,
                account_id=order.account_id,
                group_id=transaction_type_group_id,
                credit_card_object_id=order_credit_card_object.id if order_credit_card_object else None,
                user_id=user.id.replace("auth0|", ""),
                notes=other_payment.notes,
                transaction_effective_date=transaction_created_at,
            )
        )
    elif current_amount_leftover > 0:
        transaction_type = await transaction_type_crud.create(
            TransactionTypeIn(
                rent_period_id=period.id,
                payment_type=other_payment.payment_type,
                amount=current_amount_leftover,
                account_id=order.account_id,
                group_id=transaction_type_group_id,
                credit_card_object_id=order_credit_card_object.id if order_credit_card_object else None,
                user_id=user.id.replace("auth0|", ""),
                notes=other_payment.notes,
                transaction_effective_date=transaction_created_at,
            )
        )
    else:
        logger.info('amount paid insufficent, break')
        return None

    return transaction_type.id


async def _handle_lump_sum_payment(
    other_payment: OtherPayment,
    order: Order,
    outstanding_rent_periods: List[RentPeriod],
    order_credit_card_object,
    transaction_type_group_id=None,
    user=None,
):
    total_payment_amount: Decimal = other_payment.lump_sum_amount
    current_amount_leftover: Decimal = (
        total_payment_amount  # this will keep track of how much is left over to be applied to the next period
    )
    tax_rate = await _get_tax_rate(order)

    for period in outstanding_rent_periods:
        logger.info(f"Processing period {period.id}")
        logger.info(f"Current amount leftover: {current_amount_leftover}")
        period_total_balance: Decimal = period.calculated_rent_period_total_balance
        period_balance: Decimal = period.calculated_rent_period_balance
        period_fee_balance: Decimal = period.calculated_rent_period_fee_balance
        period_tax_balance: Decimal = period.calculated_rent_period_tax_balance

        order_credit_card_object_id = None
        transaction_type_uuid = await _handle_transactions(
            other_payment,
            period,
            order,
            order_credit_card_object,
            user,
            transaction_type_group_id,
            current_amount_leftover,
            period_total_balance,
        )
        amt_to_alter_total_balance: Decimal = 0
        if (
            other_payment.rent_period_fee_paid_amt
            or other_payment.rent_period_paid_amt
            or other_payment.rent_period_tax_paid_amt
        ):
            if (
                other_payment.rent_period_paid_amt > period_balance
                or other_payment.rent_period_fee_paid_amt > period_fee_balance
                or other_payment.rent_period_tax_paid_amt > period_tax_balance
            ):
                logger.info(
                    'the amounts paid per balance are greater than period owed balances, continue to next period'
                )

            is_adding = False

            amt_to_alter_total_balance = await _handle_partial_rent_pay_down(
                other_payment, period, is_adding, order_credit_card_object_id, transaction_type_uuid
            )
            logger.info(f"Amt to alter total balance: {amt_to_alter_total_balance}")

            # update other payments for each balance after paydown has already happened
            other_payment.rent_period_paid_amt -= min(other_payment.rent_period_paid_amt, period_balance)
            other_payment.rent_period_fee_paid_amt -= min(other_payment.rent_period_fee_paid_amt, period_fee_balance)
            other_payment.rent_period_tax_paid_amt -= min(other_payment.rent_period_tax_paid_amt, period_tax_balance)

            current_amount_leftover -= amt_to_alter_total_balance
            if current_amount_leftover <= 0:
                logger.info(f"Current amount leftover is {current_amount_leftover}, breaking")
                break
        else:
            logger.info(f"In Else block: {current_amount_leftover}")
            if current_amount_leftover == 0:
                logger.info(f"Current amount leftover is 0 for period {period.id}, breaking")
                break
            elif current_amount_leftover >= period_total_balance:
                await _full_period_paydown(period, transaction_type_uuid, order_credit_card_object_id)
                current_amount_leftover -= period_total_balance
            else:
                try:
                    tax_amount = 0
                    logger.info(f"Paying down balance for rent period {period.id}")
                    balance_result = await _rent_balances_paydown(
                        current_amount_leftover,
                        tax_rate,
                        transaction_type_uuid,
                        order_credit_card_object_id,
                        period,
                        'balance',
                        amt_to_alter_total_balance,
                        tax_amount,
                    )

                    current_amount_leftover = balance_result['current_amount_leftover']
                    amt_to_alter_total_balance = balance_result['amt_to_alter_total_bal']
                    tax_amount = balance_result['tax_amount']

                    logger.info(f"Paying down taxable fee for rent period {period.id}")
                    fee_result = await _rent_balances_paydown(
                        current_amount_leftover,
                        tax_rate,
                        transaction_type_uuid,
                        order_credit_card_object_id,
                        period,
                        'fee',
                        amt_to_alter_total_balance,
                        tax_amount,
                    )

                    current_amount_leftover = fee_result['current_amount_leftover']
                    amt_to_alter_total_balance = fee_result['amt_to_alter_total_bal']
                    tax_amount = fee_result['tax_amount']

                    logger.info(f"Paying down non taxable fees for rent period {period.id}")
                    non_taxable_fee_result = await _rent_balances_paydown(
                        current_amount_leftover,
                        tax_rate,
                        transaction_type_uuid,
                        order_credit_card_object_id,
                        period,
                        'non_taxable_fee',
                        amt_to_alter_total_balance,
                        tax_amount,
                    )

                    current_amount_leftover = non_taxable_fee_result['current_amount_leftover']
                    amt_to_alter_total_balance = non_taxable_fee_result['amt_to_alter_total_bal']
                    tax_amount = non_taxable_fee_result['tax_amount']

                    # finnaly pay down the tax as one entry based on all previous calculations
                    if tax_amount > 0:
                        await _handle_rent_period_tax_balance_paydown(
                            period, tax_amount, False, transaction_type_uuid, order_credit_card_object_id
                        )

                    if period_total_balance > 0:
                        paydown_amount = min(current_amount_leftover, period_total_balance)
                        amt_to_alter_total_balance += paydown_amount
                        current_amount_leftover -= paydown_amount
                        logger.debug(
                            f"Paying down {paydown_amount} from period {period.id}. Remaining credits to be used: {current_amount_leftover}"
                        )

                    await rent_period_total_balance_controller.handle_rent_period_total_balance_update(
                        period.id, period_total_balance, amt_to_alter_total_balance, False
                    )

                except Exception as e:
                    raise e


async def handle_rent_period_other_pay(
    other_payment: OtherPayment, order: Order, order_credit_card_object, transaction_type_group_id=None, user=None
):
    is_adding: bool = False
    if other_payment.lump_sum_amount and (
        other_payment.rent_period_ids is None or len(other_payment.rent_period_ids) == 0
    ):
        outstanding_rent_periods: List[RentPeriod]  # all of the periods that have balances > 0
        outstanding_rent_periods = _get_past_and_current_rent_periods(order)
        await _handle_lump_sum_payment(
            other_payment, order, outstanding_rent_periods, order_credit_card_object, transaction_type_group_id, user
        )
    else:
        # This is the partial paydown amount
        parsed_rent_periods = _get_parsed_rent_periods(order, other_payment.rent_period_ids)
        try:
            await _handle_lump_sum_payment(
                other_payment, order, parsed_rent_periods, order_credit_card_object, transaction_type_group_id, user
            )
        except Exception as e:
            raise e


async def handle_rent_period_fees_payment(
    other_payment: OtherPayment, order: Order, order_credit_card_object, user=None
):
    is_adding: bool = False
    total_payment_amount: Decimal = other_payment.lump_sum_amount
    current_amount_leftover: Decimal = (
        total_payment_amount  # this will keep track of how much is left over to be applied to the next period
    )

    tax_rate = await _get_tax_rate(order)
    outstanding_rent_periods = _get_past_and_current_rent_periods(order)

    transaction_type_group_id = str(uuid.uuid4())

    for period in outstanding_rent_periods:
        period_total_balance: Decimal = period.calculated_rent_period_total_balance

        amt_to_alter_total_bal: Decimal = 0
        order_credit_card_object_id = None
        tax_amount = 0

        transaction_type_uuid = await _handle_transactions(
            other_payment,
            period,
            order,
            order_credit_card_object,
            user,
            transaction_type_group_id,
            current_amount_leftover,
            period_total_balance,
        )

        if current_amount_leftover == 0:
            logger.info(f"Current amount leftover is 0 for fees period {period.id}, breaking")
            break
        else:
            fees_response = await _rent_balances_paydown(
                current_amount_leftover,
                tax_rate,
                transaction_type_uuid,
                order_credit_card_object_id,
                period,
                'fee',
                amt_to_alter_total_bal,
                tax_amount,
            )
            current_amount_leftover = fees_response['current_amount_leftover']
            amt_to_alter_total_bal = fees_response['amt_to_alter_total_bal']
            tax_amount = fees_response['tax_amount']

            if tax_amount > 0:
                await _handle_rent_period_tax_balance_paydown(
                    period, tax_amount, is_adding, transaction_type_uuid, order_credit_card_object_id
                )

            if period_total_balance > 0:
                paydown_amount = min(current_amount_leftover, period_total_balance)
                amt_to_alter_total_bal += paydown_amount
                current_amount_leftover -= paydown_amount
                logger.debug(
                    f"Paying down {paydown_amount} from period {period.id}. Remaining credits to be used: {current_amount_leftover}"
                )

            await rent_period_total_balance_controller.handle_rent_period_total_balance_update(
                period.id, period_total_balance, amt_to_alter_total_bal, is_adding
            )


@atomic()
async def update_rent_period_dates(rent_period_id, request, user):
    rent_period = await rent_period_crud.get_one(rent_period_id)
    await rent_period_crud.update(
        rent_period_id,
        RentPeriodIn(start_date=request.start_date, end_date=request.end_date, amount_owed=rent_period.amount_owed),
    )

    existing_order = await order_crud.get_one(rent_period.order_id)
    if not existing_order.rent_due_on_day:
        day = request.start_date.day
        await order_crud.update(
            existing_order.account_id,
            rent_period.order_id,
            OrderIn(account_id=existing_order.account_id, display_order_id=existing_order.display_order_id, rent_on_due_date=day),
        )
        existing_order.rent_due_on_day = day


    account = await account_crud.get_one(existing_order.account_id)
    if len(existing_order.rent_periods) == 1:
        initial_rent_period: RentPeriod = existing_order.rent_periods[0]

        rent_options: dict = account.cms_attributes.get("rent_options")
        rent_options['rolling_rent_periods'] = 12
        rent_options['start_date'] = initial_rent_period.start_date
        await rent_period_controller.generate_rolling_rent_periods(rent_options, initial_rent_period, existing_order)

