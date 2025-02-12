# Python imports
# import json
# Python imports
import json
from decimal import Decimal
from typing import List, Optional

# Pip imports
from loguru import logger

# Internal imports
from src.crud.account_crud import account_crud
from src.crud.tax_crud import tax_crud
from src.database.models.account import Account
from src.database.models.orders.line_item import LineItem


ORDER_OUT_LIST_KEY_INDICATOR = "orders"
SINGLE_ORDER_OUT_KEY_INDICATOR = "display_order_id"


async def get_rto_divide_by(account_id: int, rent_period: int):
    account: Account = await account_crud.get_one(account_id)
    rto_rates: List[dict] = account.cms_attributes["rent_to_own_rates"]
    rto_rate: Decimal
    for rto_rate_dict in rto_rates:
        if rto_rate_dict["months"] == rent_period:
            rto_rate = rto_rate_dict["divide_total_price_by"]
            break
    return rto_rate


async def get_tax_rate(tax_state: str, account_id: int):
    tax_rate = await tax_crud.get_tax_rate(account_id, tax_state)
    return tax_rate


async def calculated_total_rto_price(
    account_id: int, rent_period: int, tax_state: str, calculated_total_revenue: Decimal, calculated_bank_fees: Decimal
) -> Optional[Decimal]:
    total_rto_price: Decimal = 0
    tax_rate: Decimal = await get_tax_rate(tax_state, account_id)
    rto_divide_by: Decimal = await get_rto_divide_by(account_id, rent_period)

    total_revenue: Decimal = Decimal(calculated_total_revenue or 0)
    total_tax: Decimal = Decimal(total_revenue or 0) * (tax_rate)
    total_revenue_with_tax: Decimal = Decimal(total_tax or 0) + total_revenue
    total_rto_price = total_revenue_with_tax / Decimal(rto_divide_by) * Decimal(rent_period)
    total_rto_price = round(total_rto_price, 2)
    # This will just apply those bank fees on top of all the total rto price bc they are not revenue or taxable
    total_rto_price += Decimal(calculated_bank_fees or 0)

    return total_rto_price


def calcuated_monthly_price(calculated_total_rto_price: Decimal, rent_period: int) -> Optional[Decimal]:
    monthly_price: Decimal = Decimal(round((calculated_total_rto_price / rent_period), 2) or 0)
    return monthly_price


def check_is_order_out_list(response: dict) -> bool:
    """
    This will check to see if it is a list of orders or just a single one
    """
    return ORDER_OUT_LIST_KEY_INDICATOR in response


def check_is_order_out(response: dict) -> bool:
    """
    This will take the response dict and return a bool indicating
    whether this dict contains order out objects
    """
    # if there is a dictionary with a key orders, then it is a list of order outs
    if check_is_order_out_list(response):
        return True
    else:
        # but we also want to check if it is a single order out
        if SINGLE_ORDER_OUT_KEY_INDICATOR in response:
            return True
        else:
            return False

    # either way we want to return true whether they are order outs


def check_is_rto(order: dict) -> bool:
    """
    this will take each each order_out dictionary from the response and will check to see if it
    is an rto order. It will return a respective bool.
    """
    if order["type"] == "RENT_TO_OWN":
        return True
    else:
        return False


async def add_on_calculated_rto(order: dict) -> dict:
    """
    This will take the OrderOut object with rto and generate a calculated field for
    The rto
    """
    account_id: int = order["account_id"]
    order_calculated_sub_total_price: Decimal = order["calculated_sub_total_price"]  # only revenue + shipping rev
    order_calculated_fees_without_bank_fees: Decimal = order[
        "calculated_fees_without_bank_fee"
    ]  # bank fees do not get inlcuded as "revenue"
    order_total_revenue: Decimal = (
        order_calculated_sub_total_price + order_calculated_fees_without_bank_fees
    )  # this will include all the revenue from the order including fees (not bank fees)
    order_calculated_all_fees: Decimal = order["calculated_fees"]
    order_calculated_bank_fees: Decimal = (
        order_calculated_all_fees - order_calculated_fees_without_bank_fees
    )  # this will get any bank fees that have been assessed if any
    line_items: List[LineItem] = order["line_items"]
    if len(line_items) > 0:
        li: LineItem = line_items[0]
        tax_state: str = li["product_state"]
        rent_period: int = li["rent_period"]

        total_rto_price: Decimal = await calculated_total_rto_price(
            account_id, rent_period, tax_state, order_total_revenue, order_calculated_bank_fees
        )
        monthly_price: Decimal = calcuated_monthly_price(total_rto_price, rent_period)

        order["calculated_rto_price"] = float(total_rto_price)
        order["calculated_monthly_price"] = float(monthly_price)
    else:
        order["calculated_rto_price"] = 0
        order["calculated_monthly_price"] = 0

    return order


async def order_out_rto_checks(order: dict) -> dict:
    """
    This will take care of checking whether the order is an rto and if it is
    then it will add the appropriate calculated fields to that object, but if not
    it will continue on
    """
    is_rto: bool = check_is_rto(order)
    if is_rto:
        try:
            order = await add_on_calculated_rto(order)
        except Exception as e:
            logger.info(f"Error running the order_out_rto_checks: {e}")


class async_iterator_wrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


async def order_out_filter(resp_body) -> bytearray:
    """
    This function will run all of the logic necessary to handle modifications to order out objects
    """
    is_order_out: bool = False
    is_order_out_list: bool = False
    try:
        try:
            decoded_resp = resp_body[0].decode()
        except UnicodeDecodeError:
            return resp_body
        # converting the json to a dictionary so that we can manipulate it
        resp_body_dict: dict = json.loads(decoded_resp)
        # logger.info(resp_body_dict)

        # make the modifications here!
        is_order_out = check_is_order_out(resp_body_dict)
        if is_order_out:
            is_order_out_list = check_is_order_out_list(resp_body_dict)
            if is_order_out_list:
                pass
                # we don't need any of this information whenever we initially load the get by status type
                # this data is only important if we are clicking on any given order
                # for order in resp_body_dict["orders"]:
                #     await order_out_rto_checks(order)
            else:
                await order_out_rto_checks(resp_body_dict)

            # getting the dict back to json for the response
            resp_body = json.dumps(resp_body_dict)
            # Taking the json and converting it to bytes
            resp_body = resp_body.encode("utf-8")
            # putting these bytes into a single item list for standard procedure
            resp_body = [resp_body]

    except (json.JSONDecodeError, IndexError, TypeError):
        # This will catch the error that occurs when you try to decode an object that is not decodable
        # for example, some of these resp_body objs come through as [] and so that means they are not decodable
        # or if they are just [b'OK'] then it would work int eh json.loads
        resp_body = resp_body

    return resp_body
