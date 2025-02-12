# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import transaction_type
from src.dependencies import auth
from src.schemas.transaction_type import TransactionTypeIn, TransactionTypeInDto, TransactionTypeOut


router = APIRouter(
    tags=["transaction_type"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/transaction_type", response_model=TransactionTypeOut)
async def create_transaction_type(
    transaction_t: TransactionTypeIn, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    return await transaction_type.create_transaction_type(transaction_t, user, background_tasks=background_tasks)


@router.delete("/transaction_type/{transaction_type_id}")
async def delete_transaction_type(transaction_type_id: str, user: Auth0User = Depends(auth.get_user)):
    return await transaction_type.delete_transaction_type(transaction_type_id, user)


@router.get("/transaction_types_grouped/{transaction_id}")
async def get_transaction_types_grouped(transaction_id: str, user: Auth0User = Depends(auth.get_user)):
    return await transaction_type.get_transaction_types_grouped(transaction_id, user)


@router.patch("/transaction_type/{transaction_type_id}", response_model=TransactionTypeOut)
async def update_transaction_type(
    transaction_type_id: str, transaction_t: TransactionTypeInDto, user: Auth0User = Depends(auth.get_user)
):
    return await transaction_type.update_transaction_type(transaction_type_id, transaction_t, user)


@router.get("/get_order_transaction_types/{order_id}", response_model=List[TransactionTypeOut])
async def get_order_transaction_type(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await transaction_type.get_order_transaction_types(order_id, user)


@router.get("/get_period_transaction_types/{period_id}", response_model=List[TransactionTypeOut])
async def get_period_transaction_type(period_id: str, user: Auth0User = Depends(auth.get_user)):
    return await transaction_type.get_period_transaction_types(period_id, user)
