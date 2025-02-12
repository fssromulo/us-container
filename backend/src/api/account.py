# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import account as account_controller
from src.dependencies import auth
from src.schemas.accounts import AccountInSchema, AccountOutSchema, UpdateAccount
from src.schemas.token import Status


router = APIRouter(
    tags=["account"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/accounts", response_model=List[AccountOutSchema])
async def get_accounts():
    return await account_controller.get_all_accounts()


@router.get("/account", response_model=AccountOutSchema)
@cache(namespace="account", expire=60 * 10)
async def get_account(user: Auth0User = Depends(auth.get_user)) -> AccountOutSchema:
    try:
        return await account_controller.get_account(user)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Account does not exist")


@router.post("/account", response_model=AccountOutSchema)
async def create_account(account: AccountInSchema) -> AccountOutSchema:
    await FastAPICache.clear(namespace="account")
    return await account_controller.create_account(account)


@router.patch("/account", response_model=AccountOutSchema, responses={404: {"model": HTTPNotFoundError}})
async def update_account(
    account: UpdateAccount,
    user: Auth0User = Depends(auth.get_user),
) -> AccountOutSchema:
    await FastAPICache.clear(namespace="account")
    return await account_controller.update_account(user, account)

@router.patch("/account/attributes", response_model=AccountOutSchema, responses={404: {"model": HTTPNotFoundError}})
async def update_account(
    account: UpdateAccount,
    user: Auth0User = Depends(auth.get_user),
) -> AccountOutSchema:
    await FastAPICache.clear(namespace="account")
    return await account_controller.update_account_attributes(user, account)

@router.delete("/account", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_account(account_id: int):
    pass
