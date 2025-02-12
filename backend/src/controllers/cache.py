# Python imports
from typing import List

# Internal imports
from src.auth.auth import Auth0User
from src.crud.account_crud import account_crud
from src.schemas.accounts import AccountInSchema, AccountOutSchema, UpdateAccount
from fastapi_cache import FastAPICache

async def clear_all() -> AccountOutSchema:
    await FastAPICache.clear(namespace="coupon_code")
    await FastAPICache.clear(namespace="drivers")
    await FastAPICache.clear(namespace="locations")
    await FastAPICache.clear(namespace="commissions")
    await FastAPICache.clear(namespace="rankings")
    await FastAPICache.clear(namespace="roles")
    await FastAPICache.clear(namespace="users")
    return True