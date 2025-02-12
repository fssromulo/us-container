# Python imports
from typing import List

# Pip imports
from loguru import logger

# Internal imports
from src.auth.auth import Auth0User
from src.crud.account_crud import account_crud
from src.schemas.accounts import AccountInSchema, AccountOutSchema, UpdateAccount


async def save_account(account: UpdateAccount, account_id: str = None) -> AccountOutSchema:
    account_dict = account.dict(exclude_unset=True)
    logger.info(account_dict)

    if account_id:
        saved_account = await account_crud.update(account_id, account_id, AccountInSchema(**account_dict))
    else:
        saved_account = await account_crud.create(AccountInSchema(**account_dict))

    return saved_account


async def get_all_accounts() -> List[AccountOutSchema]:
    return await account_crud.get_all()


async def create_account(account: AccountInSchema) -> AccountOutSchema:
    return await account_crud.create(account)


async def get_account(user: Auth0User) -> List[AccountOutSchema]:
    return await account_crud.get_one(user.app_metadata.get("account_id"))


async def get_account_by_id(account_id: int) -> List[AccountOutSchema]:
    return await account_crud.get_one(account_id)


async def update_account(user: Auth0User, account: UpdateAccount) -> AccountOutSchema:
    return await save_account(account, user.app_metadata.get("account_id"))


async def update_account_attributes(user: Auth0User, account: UpdateAccount) -> AccountOutSchema:
    return await account_crud.update_attributes(user.app_metadata.get("account_id"), account)
