
# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import order_fee_balance
from src.dependencies import auth
from src.schemas.order_fee_balance import OrderFeeBalanceOut, OrderFeeBalanceIn

router = APIRouter(
    tags=["order_fee_balance"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/order_fee_balance", response_model=OrderFeeBalanceOut)
async def create_order_fee_balance(order_fee_balance: OrderFeeBalanceIn, user: Auth0User = Depends(auth.get_user)):
    return await order_fee_balance.create_order_fee_balance(order_fee_balance, user)
