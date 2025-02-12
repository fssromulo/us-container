# Python imports
from decimal import Decimal

# Internal imports
from src.auth.auth import Auth0User
from src.crud.order_crud import order_crud
from src.crud.order_tax_crud import order_tax_crud
from src.crud.total_order_balance_crud import total_order_balance_crud
from src.database.models.order_tax import OrderTax
from src.database.models.orders.order import Order
from src.schemas.order_tax import OrderTaxIn, OrderTaxOut


async def create_order_tax(order_tax: OrderTaxIn, user: Auth0User) -> OrderTaxOut:
    """
    This function will handle the creation of the order tax obj while also handling the order balance update
    """
    existing_order: Order = await order_crud.get_one(order_tax.order_id)
    saved_order_tax: OrderTax = await order_tax_crud.create(order_tax)

    tax_diff: Decimal = round(Decimal(saved_order_tax.tax_amount or 0) - existing_order.calculated_order_tax, 2)
    is_adding: bool = True if tax_diff > 0 else False
    await total_order_balance_crud.handle_order_balance_update(existing_order.id, abs(tax_diff), is_adding)

    return saved_order_tax
