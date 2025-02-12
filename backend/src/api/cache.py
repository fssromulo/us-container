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
from src.controllers import cache as cache_controller
from src.dependencies import auth
from src.schemas.accounts import AccountInSchema, AccountOutSchema, UpdateAccount
from src.schemas.token import Status

router = APIRouter(
    tags=["cache"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.delete("/cache",)
async def get_accounts():
    return await cache_controller.clear_all()
