# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import vendors
from src.dependencies import auth
from src.schemas.token import Status
from src.schemas.vendor_types import VendorTypeOutSchema
from src.schemas.vendors import UpdateVendor, VendorOutSchema


router = APIRouter(
    tags=["vendors"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/vendor_type", response_model=List[VendorTypeOutSchema])
async def get_all_vendor_types(user: Auth0User = Depends(auth.get_user)) -> List[VendorTypeOutSchema]:
    return await vendors.get_all_vendor_types(user)


@router.get("/vendor", response_model=List[VendorOutSchema])
async def get_all_vendor(user: Auth0User = Depends(auth.get_user)) -> List[VendorOutSchema]:
    return await vendors.get_all_vendor(user)


@router.get("/vendor/{vendor_id}", response_model=VendorOutSchema)
async def get_vendor(vendor_id: str, user: Auth0User = Depends(auth.get_user)) -> VendorOutSchema:
    get_vendors = [p for p in user.permissions if p == "read:inventory-vendors"]
    if not get_vendors:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to retrieve vendors",
        )
    result = await vendors.get_vendor(vendor_id, user)
    return result


@router.post("/vendor", response_model=VendorOutSchema, status_code=status.HTTP_201_CREATED)
async def create_vendor(vendor: UpdateVendor, user: Auth0User = Depends(auth.get_user)) -> VendorOutSchema:
    create_vendors = [p for p in user.permissions if p == "create:inventory-vendors"]
    if not create_vendors:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create vendors",
        )
    return await vendors.create_vendor(vendor, user)


@router.patch(
    "/vendor/{vendor_id}",
    response_model=VendorOutSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_vendor(
    vendor_id: str, vendor: UpdateVendor, user: Auth0User = Depends(auth.get_user)
) -> VendorOutSchema:
    # update_vendors = [p for p in user.permissions if p == "update:inventory-vendors"]
    # if not update_vendors:
    #   raise HTTPException(
    #       status_code=status.HTTP_403_FORBIDDEN,
    #       detail="You do not have permission to update vendors",
    #     )
    return await vendors.update_vendor(vendor_id, vendor, user)


@router.delete(
    "/vendor/{vendor_id}", response_model=Status, responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}}
)
async def delete_vendor(vendor_id: str, user: Auth0User = Depends(auth.get_user)) -> Status:
    delete_vendors = [p for p in user.permissions if p == "delete:inventory-vendors"]
    if not delete_vendors:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete vendors",
        )
    return await vendors.delete_vendor(vendor_id, user)
