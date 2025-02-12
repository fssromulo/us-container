# Python imports
import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

# Pip imports
from loguru import logger

# Internal imports
from src.controllers import rent_period_fee_balance as rent_period_fee_balance_controller
from src.controllers import rent_period_tax as rent_period_tax_controller
from src.controllers import rent_period_total_balance as rent_period_total_balance_controller
from src.controllers import subtotal_balance as subtotal_balance_controller
from src.controllers import tax_balance as tax_balance_controller
from src.crud.account_crud import account_crud
from src.crud.coupon_code_crud import coupon_code_crud
from src.crud.coupon_code_order_crud import coupon_code_order_crud
from src.crud.coupon_line_item_value_crud import coupon_line_item_crud
from src.crud.order_crud import order_crud
from src.crud.order_tax_crud import order_tax_crud
from src.crud.tax_crud import tax_crud
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.database.models.order_tax import OrderTax
from src.database.models.orders.line_item import LineItem
from src.database.models.orders.order import Order
from src.database.models.rent_period import RentPeriod
from src.database.models.rent_period_tax import RentPeriodTax
from src.schemas.coupon_line_item_value import CouponLineItemValueIn
from src.schemas.order_tax import OrderTaxIn
from src.schemas.orders import OrderOut
from src.schemas.rent_period_fee_balance import RentPeriodFeeBalanceIn
from src.schemas.rent_period_tax import RentPeriodTaxIn
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn
from src.schemas.tax_balance import TaxBalanceIn
from src.schemas.total_order_balance import TotalOrderBalanceIn


async def handle_create_order_balance(new_balance: Decimal, order_id: str):
    create_order_balance = TotalOrderBalanceIn(remaining_balance=new_balance, order_id=order_id)
    await total_order_balance_crud.create(create_order_balance)


def add_or_subtract(a, b, is_adding):
    return a + b if is_adding else a - b


async def fetch_applied_coupon_amount(order: OrderOut, line_item: LineItem, applied_coupon_id: str, is_adding: True):
    applied_coupons = await coupon_code_order_crud.get_all_by_order_id(order.account_id, order.id)
    discounted_amount = 0
    for coupon in applied_coupons:
        if is_adding == False and coupon.id == applied_coupon_id:
            # We are adding the new coupon no need to re-add its value
            continue
        if line_item.revenue >= coupon.coupon.minimum_discount_threshold:
            # for percentage coupons get value from line item value
            if coupon.coupon.percentage:
                pass
            else:
                discounted_amount = discounted_amount + coupon.amount
        pass


def fetch_revenue_without_discount(line_item: LineItem):
    total = 0
    total = line_item.revenue + total
    for coupon in line_item.coupon_line_item_values:
        total = total + coupon.amount
    return total


async def line_item_discounted_revenue_adjustment(
    order: OrderOut, is_adding: True, coupon_id: str, coupon_code_order_id: str
):
    coupon = await coupon_code_crud.get_one(order.account_id, coupon_id)
    line_items = await LineItem.filter(order_id=order.id).prefetch_related('coupon_line_item_values').all()
    line_items_update: List[LineItem] = []
    coupon_line_items: List[CouponLineItemValueIn] = []
    coupon_line_item_ids = []
    change_amount_pre_tax = Decimal(0)
    get_discount = lambda data, x: next((item.amount for item in data if item.coupon_code_order_id == x), 0)
    for line_item in line_items:
        line_item_revenue = (
            fetch_revenue_without_discount(line_item)
            if len(line_item.coupon_line_item_values) == 0
            else line_item.revenue
        )

        discount_amount = Decimal(0)
        discount_modified = False
        # if line_item_revenue >= coupon.minimum_discount_threshold:

        if is_adding:  # we dont have to check the min discount threshold if we are removing the coupon
            discount_amount = get_discount(line_item.coupon_line_item_values, coupon_code_order_id)
            discount_modified = True
        elif is_adding == False and line_item_revenue >= coupon.minimum_discount_threshold:
            discount_modified = True
            if coupon.percentage:
                discount_amount = line_item_revenue * Decimal(coupon.percentage) / Decimal(100)
            else:
                discount_amount = coupon.amount
            # Check line item type and apply relevant discounts
            # logger.info(discount_amount)
        if discount_modified:  # A coupon was added or removed
            if line_item.product_type is not None and line_item.product_type == "CONTAINER_ACCESSORY":
                # Accessory
                logger.info("This is an accessory")
                if coupon.category in ['accessories_only', 'both']:
                    logger.info("Applying coupon")
                    change_amount_pre_tax = change_amount_pre_tax + discount_amount
                    line_items_update.append(
                        LineItem(
                            **{
                                "id": line_item.id,
                                "revenue": add_or_subtract(line_item.revenue, abs(discount_amount), is_adding),
                            }
                        )
                    )
                    if is_adding:
                        coupon_line_item_ids.append(str(line_item.id))
                    else:
                        coupon_line_items.append(
                            CouponLineItemValueIn(
                                id=uuid.uuid4(),
                                line_item_id=line_item.id,
                                coupon_code_order_id=coupon_code_order_id,
                                amount=discount_amount,
                            )
                        )

            else:
                # Container
                logger.info("This is a container")
                if coupon.category == 'both' or coupon.category != 'accessories_only':
                    logger.info("Applying coupon")
                    change_amount_pre_tax = change_amount_pre_tax + discount_amount
                    line_items_update.append(
                        LineItem(
                            **{
                                "id": line_item.id,
                                "revenue": add_or_subtract(line_item.revenue, abs(discount_amount), is_adding),
                            }
                        )
                    )
                    if is_adding:
                        coupon_line_item_ids.append(str(line_item.id))
                    else:
                        coupon_line_items.append(
                            CouponLineItemValueIn(
                                id=uuid.uuid4(),
                                line_item_id=line_item.id,
                                coupon_code_order_id=coupon_code_order_id,
                                amount=discount_amount,
                            )
                        )

    if len(line_items_update) == 0:
        return

    # we only want the subtotal and fees. not the tax
    await LineItem.bulk_update(line_items_update, ['revenue'], len(line_items_update))
    if len(coupon_line_items) > 0:
        await coupon_line_item_crud.bulk_create(coupon_line_items, len(coupon_line_items))
    else:
        # delete
        await coupon_line_item_crud.delete_all_in(coupon_line_item_ids, coupon_code_order_id)
    order = await order_crud.get_one(order.id)

    account = await account_crud.get_one(order.account_id)

    change_amount_tax = Decimal(0)
    if account.cms_attributes.get("charge_tax", True):
        tax_rate = order.calculated_order_tax_rate
        adjusted_tax: Decimal = change_amount_pre_tax * tax_rate
        adjusted_tax = Decimal(
            adjusted_tax.quantize(
                Decimal(
                    ".01",
                ),
                rounding=ROUND_HALF_UP,
            )
        )
        new_tax_amt: Decimal = add_or_subtract(order.calculated_order_tax, abs(adjusted_tax), is_adding)
        await handle_order_tax_update(order.id, abs(new_tax_amt))
        await tax_balance_controller.handle_tax_balance_paydown(order, adjusted_tax, is_adding)
        change_amount_tax = adjusted_tax

    change_to_blance: Decimal = change_amount_pre_tax + change_amount_tax

    await order_balance_adjustment(order, change_to_blance, is_adding)
    await subtotal_balance_controller.handle_subtotal_balance_paydown(
        order, change_amount_pre_tax, is_adding, None, None
    )


async def line_item_revenue_adjustment(order: OrderOut, amount: Decimal, is_adding: True, minimum_threshold: int = 0):
    line_items = order.line_items
    line_items_update = [
        LineItem(**{"id": line_item.id, "revenue": add_or_subtract(line_item.revenue, abs(amount), is_adding)})
        for line_item in line_items
        if line_item.calculated_total_revenue >= minimum_threshold
    ]

    if len(line_items_update) == 0:
        return

    # we only want the subtotal and fees. not the tax
    await LineItem.bulk_update(line_items_update, ['revenue'], len(line_items_update))
    order = await order_crud.get_one(order.id)

    account = await account_crud.get_one(order.account_id)

    line_items_count = len(
        [line_item for line_item in line_items if line_item.calculated_total_revenue >= minimum_threshold]
    )
    change_amount_pre_tax = amount * Decimal(line_items_count)

    change_amount_tax = 0
    if account.cms_attributes.get("charge_tax", True):
        change_amount_tax = await handle_order_tax_calc(order, change_amount_pre_tax, is_adding)

    change_to_blance: Decimal = change_amount_pre_tax + change_amount_tax

    await order_balance_adjustment(order, change_to_blance, is_adding)
    await subtotal_balance_controller.handle_subtotal_balance_paydown(
        order, change_amount_pre_tax, is_adding, None, None
    )


async def order_balance_adjustment(order: Order, amount: Decimal, is_adding: bool = True):
    current_balance: Decimal = order.calculated_remaining_order_balance
    new_balance: Decimal = add_or_subtract(current_balance, abs(amount), is_adding)

    await handle_create_order_balance(new_balance, order.id)


async def rent_period_fee_balance_adjustment(
    rent_period: RentPeriod, fee_amount: Decimal, fee_with_tax_amount: Decimal, is_adding: bool = True
):
    current_balance: Decimal = rent_period.calculated_rent_period_fee_balance
    new_balance: Decimal = add_or_subtract(current_balance, abs(fee_amount), is_adding)

    create_obj: RentPeriodFeeBalanceIn = RentPeriodFeeBalanceIn(
        remaining_balance=new_balance, rent_period_id=rent_period.id
    )

    await rent_period_fee_balance_controller.create_rent_period_fee_balance(create_obj)

    await rent_period_total_balance_adjustment(rent_period, abs(fee_with_tax_amount), is_adding)


async def rent_period_total_balance_adjustment(rent_period: RentPeriod, abs_amount: Decimal, is_adding: bool = True):
    current_balance: Decimal = rent_period.calculated_rent_period_total_balance
    new_balance: Decimal = add_or_subtract(current_balance, abs_amount, is_adding)

    create_obj: RentPeriodTotalBalanceIn = RentPeriodTotalBalanceIn(
        remaining_balance=new_balance, rent_period_id=rent_period.id
    )

    await rent_period_total_balance_controller.create_rent_period_total_balance(create_obj)


async def handle_order_tax_update(order_id: str, new_tax: Decimal) -> Decimal:
    # grab order so that we can get the most recent calculated remaining balance value
    create_order_tax: OrderTaxIn = OrderTaxIn(tax_amount=new_tax, order_id=order_id)
    new_order_tax: OrderTax = await order_tax_crud.create(create_order_tax)

    return new_order_tax.tax_amount


async def handle_order_tax_calc(existing_order: Order, new_amount_to_calculate: Decimal, is_adding: bool) -> Decimal:
    tax_state: str = existing_order.address.state
    tax_rate: Decimal = await tax_crud.get_tax_rate(existing_order.account_id, tax_state)
    adjusted_tax: Decimal = new_amount_to_calculate * tax_rate
    adjusted_tax = Decimal(
        adjusted_tax.quantize(
            Decimal(
                ".01",
            ),
            rounding=ROUND_HALF_UP,
        )
    )
    new_tax_amt: Decimal = add_or_subtract(existing_order.calculated_order_tax, abs(adjusted_tax), is_adding)
    await handle_order_tax_update(existing_order.id, abs(new_tax_amt))
    await tax_balance_controller.handle_tax_balance_paydown(existing_order, adjusted_tax, is_adding)

    return adjusted_tax


async def handle_rent_period_tax_update(rent_period_id: str, new_tax: Decimal) -> Decimal:
    create_rent_period_tax: RentPeriodTaxIn = RentPeriodTaxIn(rent_period_id=rent_period_id, tax_amount=new_tax)
    new_rent_period_tax: RentPeriodTax = await rent_period_tax_controller.create_rent_period_tax(create_rent_period_tax)

    return new_rent_period_tax.tax_amount


async def handle_rent_period_tax_calc(
    existing_rent_period: RentPeriod, new_amount_to_calculate: Decimal, is_adding: bool
) -> Decimal:
    existing_order: Order = await order_crud.get_one(existing_rent_period.order_id)
    tax_state: str = (
        existing_order.address.state
        if existing_order.address
        else existing_order.single_customer.customer_contacts[0].customer_address.state
    )
    tax_rate: Decimal = await tax_crud.get_tax_rate(existing_order.account_id, tax_state)
    adjusted_tax: Decimal = new_amount_to_calculate * tax_rate
    adjusted_tax = Decimal(
        adjusted_tax.quantize(
            Decimal(
                ".01",
            ),
            rounding=ROUND_HALF_UP,
        )
    )
    new_tax_amt: Decimal = add_or_subtract(
        existing_rent_period.calculated_rent_period_tax, abs(adjusted_tax), is_adding
    )
    await handle_rent_period_tax_update(existing_rent_period.id, new_tax_amt)
    return adjusted_tax
