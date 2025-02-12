from typing import List

from fastapi import HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from src.schemas.tax import (
    TaxOutSchema,
    TaxInSchema,
    CreateOrUpdateTax
)

from src.crud.tax_crud import tax_crud
from src.schemas.token import Status
from src.auth.auth import Auth0User
from src.dependencies import auth
from src.controllers import tax

async def get_container_taxs(user: Auth0User):
    return await tax_crud.get_all(user.app_metadata["account_id"])

async def get_container_tax(tax_id: str, user: Auth0User) -> TaxOutSchema:
    try:
        return await tax_crud.get_one(user.app_metadata["account_id"], tax_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Container tax does not exist",
        )
    
async def get_container_tax(tax_id: str, user: Auth0User) -> TaxOutSchema:
    try:
        return await tax_crud.get_one(user.app_metadata["account_id"], tax_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Container tax does not exist",
        )


async def save_tax(tax, user, tax_id=None):
    tax_dict = tax.dict(exclude_unset=True)
    tax_dict["account_id"] = user.app_metadata["account_id"]

    if tax_id:
        saved_tax = await tax_crud.update(user.app_metadata["account_id"], tax_id,
            TaxInSchema(**tax_dict)
        )
    else:
        saved_tax = await tax_crud.create(TaxInSchema(**tax_dict))

    return saved_tax

async def create_tax(
    container_tax: CreateOrUpdateTax,
    user: Auth0User
) -> TaxOutSchema:
    return await save_tax(container_tax, user)

async def get_container_taxs(user: Auth0User):
    return await tax_crud.get_all(user.app_metadata["account_id"])

async def get_container_tax(tax_id: str, user: Auth0User) -> TaxOutSchema:
    try:
        return await tax_crud.get_one(user.app_metadata["account_id"], tax_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Container tax does not exist",
        )
    
async def create_tax(
    container_tax: CreateOrUpdateTax,
    user: Auth0User
) -> TaxOutSchema:
    return await save_tax(container_tax, user)

async def update_tax(
    tax_id: str,
    container_tax: CreateOrUpdateTax,
    user: Auth0User
) -> TaxOutSchema:
    return await save_tax(container_tax, user, tax_id)

async def delete_container_tax(tax_id: str, user: Auth0User):
    res = await tax_crud.delete_one(user.app_metadata["account_id"], tax_id)
    return Status(message=f"Deleted tax")