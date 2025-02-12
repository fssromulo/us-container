# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import tax
from src.crud.tax_crud import tax_crud
from src.dependencies import auth
from src.schemas.tax import CreateOrUpdateTax, TaxOutSchema
from src.schemas.token import Status


router = APIRouter(
    tags=["tax"],
    dependencies=[Depends(auth.implicit_scheme)],
)


@router.get(
    "/taxes",
    response_model=List[TaxOutSchema],
)
async def get_container_taxs(user: Auth0User = Depends(auth.get_user)):
    return await tax.get_container_taxs(user)


@router.post(
    "/tax",
    response_model=TaxOutSchema,
)
async def create_tax(container_tax: CreateOrUpdateTax, user: Auth0User = Depends(auth.get_user)) -> TaxOutSchema:
    return await tax.create_tax(container_tax, user)


@router.get(
    "/tax/{tax_id}",
    response_model=TaxOutSchema,
)
async def get_container_tax(tax_id: str, user: Auth0User = Depends(auth.get_user)) -> TaxOutSchema:
    return await tax.get_container_tax(tax_id, user)


@router.post(
    "/tax",
    response_model=TaxOutSchema,
)
async def create_tax(container_tax: CreateOrUpdateTax, user: Auth0User = Depends(auth.get_user)) -> TaxOutSchema:
    return await tax.create_tax(container_tax, user)


@router.patch(
    "/tax/{tax_id}",
    response_model=TaxOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_tax(
    tax_id: str, container_tax: CreateOrUpdateTax, user: Auth0User = Depends(auth.get_user)
) -> TaxOutSchema:
    return await tax.update_tax(tax_id, container_tax, user)


@router.delete(
    "/tax/{tax_id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
)
async def delete_container_tax(tax_id: str, user: Auth0User = Depends(auth.get_user)):
    return await tax.delete_container_tax(tax_id, user)
    res = await tax_crud.delete_one(user.app_metadata["account_id"], tax_id)
    return Status(message=f"Deleted tax")
