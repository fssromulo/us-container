# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.dependencies import auth
from src.schemas.order_tax import OrderTaxIn, OrderTaxOut


router = APIRouter(
    tags=["order_tax"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/order_tax", response_model=OrderTaxOut)
async def create_order_tax(order_tax: OrderTaxIn, user: Auth0User = Depends(auth.get_user)):
    return await order_tax.create_order_tax(order_tax, user)
