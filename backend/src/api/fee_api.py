# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import fee_controller
from src.crud.account_crud import account_crud
from src.dependencies import auth
from src.schemas.fee import FeeIn, FeeInUpdate, FeeOut, UpdateFee
from src.schemas.token import Status


router = APIRouter(
    tags=["fee"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/fee", response_model=Status)
async def create_fee(fee: List[FeeIn], user: Auth0User = Depends(auth.get_user)):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    return await fee_controller.create_fee(fee, user, account)


@router.patch("/fee", response_model=Status)
async def update_fee(fees: List[UpdateFee], user: Auth0User = Depends(auth.get_user)):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    return await fee_controller.update_fee(fees, user, account)


@router.delete("/fee/{fee_id}", response_model=Status)
async def delete_fee(fee_id: str, user: Auth0User = Depends(auth.get_user)):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    return await fee_controller.delete_fee(fee_id, user, account)


@router.delete("/fee_rush/{order_id}", response_model=Status)
async def delete_rush_fee(order_id: str, user: Auth0User = Depends(auth.get_user)):
    account = await account_crud.get_one(user.app_metadata['account_id'])
    return await fee_controller.delete_rush_fee(order_id, user, account)
