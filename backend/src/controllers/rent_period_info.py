# internal imports
# Python imports
from datetime import datetime, timedelta
from typing import List
from decimal import Decimal

# Internal imports
from src.controllers import balance as balance_controller
from src.controllers import rent_period as rent_period_controller
from src.controllers import rent_period_balance as rent_period_balance_controller
from src.controllers import rent_period_tax as rent_period_tax_controller
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.order_crud import OrderCRUD
from src.database.models.rent_period import RentPeriod
from src.database.models.rent_period_tax import RentPeriodTax
from src.database.models.orders.order import Order
from src.schemas.rent_period import RentPeriodIn
from src.schemas.rent_period_balance import RentPeriodBalanceIn
from src.schemas.rent_period_info import UpdateRentPeriodInfo
from src.schemas.rent_period_tax import RentPeriodTaxIn
from src.database.models.account import Account
from src.crud.rent_period_tax_balance_crud import RentPeriodTaxBalanceIn, rent_period_tax_balance_crud
order_crud = OrderCRUD()


def is_date_in_past(target_date):
    current_date = datetime.now()
    if not target_date:
        return False
    return target_date.replace(tzinfo=None) < current_date.replace(tzinfo=None)

def period_is_paid_or_partially_paid(rent_period):
    return rent_period.calculated_rent_period_total_balance == 0 or (
        rent_period.calculated_rent_period_total_balance != 0
        and rent_period.transaction_type_rent_period is not None
        and len(rent_period.transaction_type_rent_period) > 0
    )

async def generate_new_rental_period(order_id, number_of_period):
    order: Order = await order_crud.get_one(order_id)
    account: Account = await account_crud.get_one(order.account_id)
    rent_options: dict = account.cms_attributes.get("rent_options")
    rent_options['rolling_rent_periods'] = number_of_period
    rent_periods = sorted(order.rent_periods, key=lambda x: x.start_date)
    rent_options['start_date'] = rent_periods[0].start_date
    await rent_period_controller.generate_rolling_rent_periods(rent_options, rent_periods[0], order, quick_rent=False, drop_off=0, pickup=0,
                                                                number_of_periods=len(rent_periods) - 1 if len(rent_periods) > 1 else 1)
    return True

async def update_rent_period_price(order_id, price):
    order: Order = await order_crud.get_one(order_id)
    rent_periods: List[RentPeriod] = order.rent_periods
    account = await account_crud.get_one(account_id=order.account_id)
    rent_options: dict = account.cms_attributes.get("rent_options")
    for rent_period in rent_periods:
        if not period_is_paid_or_partially_paid(rent_period):
            rent_period.amount_owed = price

            update_rent_period: RentPeriodIn = RentPeriodIn(
                start_date=rent_period.start_date,
                end_date=rent_period.end_date,
                order_id=order.id,
                amount_owed=rent_period.amount_owed,
            )

            await rent_period_controller.update_rent_period(update_rent_period, rent_period_id=rent_period.id)

            saved_rent_period_balance = await rent_period_controller.handle_create_rent_period_balance(
                rent_period.amount_owed, rent_period_id=rent_period.id
            )

            saved_rent_period_fee_balance_amt: Decimal = rent_period.calculated_rent_period_fee_balance

            rent_period_tax = await rent_period_controller.calculate_rent_period_tax(
                order,
                account.id,
                saved_rent_period_fee_balance_amt,
                saved_rent_period_balance.remaining_balance,
            )

            saved_rent_tax: RentPeriodTax = await rent_period_controller.handle_create_rent_period_tax(
                rent_period_tax, rent_period.id
            )

            rent_options["rent_period_paid"] = (
                True
                if rent_options.get("rent_period_paid", None) and rent_period.start_date.date() <= datetime.now().date()
                else False
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

            await rent_period_controller.handle_create_rent_period_total_balance(
                rent_period_total_balance, rent_period.id
            )
    return True


async def update_rent_period_info(rent_period_info: UpdateRentPeriodInfo):
    current_rent_period: RentPeriod = await rent_period_controller.get_rent_period(rent_period_info.rent_period_id)
    total_amt_changed: Decimal = 0
    is_adding: bool
    saved_rent_period_balance = None

    try:
        if rent_period_info.balance_amt is not None:
            balance_amt: Decimal = rent_period_info.balance_amt
            total_amt_changed += balance_amt - current_rent_period.calculated_rent_period_balance
            create_rent_period_balance: RentPeriodBalanceIn = RentPeriodBalanceIn(
                remaining_balance=balance_amt, rent_period_id=current_rent_period.id
            )
            saved_rent_period_balance = await rent_period_balance_controller.create_rent_period_balance(
                create_rent_period_balance
            )

        if rent_period_info.balance_amt is not None and rent_period_info.tax_amt is None:
            exsiting_order: Order = await order_crud.get_one(current_rent_period.order_id)
            rent_period_tax = await rent_period_controller.calculate_rent_period_tax(
                exsiting_order,
                exsiting_order.account_id,
                current_rent_period.calculated_rent_period_fee_balance,
                saved_rent_period_balance.remaining_balance,
            )

            saved_rent_tax: RentPeriodTax = await rent_period_controller.handle_create_rent_period_tax(
                rent_period_tax, current_rent_period.id
            )
            total_amt_changed += saved_rent_tax.tax_amount - current_rent_period.calculated_rent_period_tax

        if rent_period_info.tax_amt is not None:
            tax_amt: Decimal = rent_period_info.tax_amt
            total_amt_changed += tax_amt - current_rent_period.calculated_rent_period_tax_balance
            create_rent_period_tax: RentPeriodTaxIn = RentPeriodTaxIn(
                tax_amount=tax_amt, rent_period_id=current_rent_period.id
            )
            await rent_period_tax_controller.create_rent_period_tax(create_rent_period_tax)


            create_obj: RentPeriodTaxBalanceIn = RentPeriodTaxBalanceIn(
                balance=tax_amt,
                rent_period_id=current_rent_period.id,
                tax_rate=0,
                transaction_type_id=None,
                order_credit_card_id=None,
            )
            await rent_period_tax_balance_crud.create(create_obj)

        if rent_period_info.amount_owed is not None:
            update_rent_period: RentPeriodIn = RentPeriodIn(
                amount_owed=rent_period_info.amount_owed,
            )
            await rent_period_controller.update_rent_period(update_rent_period, rent_period_id=current_rent_period.id)
            amount_owed: Decimal = rent_period_info.amount_owed
            total_amt_changed += amount_owed - current_rent_period.amount_owed
            await rent_period_controller.handle_create_rent_period_balance(
                rent_period_info.amount_owed, rent_period_id=current_rent_period.id
            )

        is_adding = total_amt_changed > 0
        await balance_controller.rent_period_total_balance_adjustment(
            current_rent_period, abs(total_amt_changed), is_adding
        )

    except Exception as e:
        raise e
