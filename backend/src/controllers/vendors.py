# Python imports
from typing import List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.note_crud import note_crud
from src.crud.vendor_crud import vendor_crud
from src.crud.vendor_type_crud import vendor_type_crud
from src.schemas.notes import NoteInSchema
from src.schemas.token import Status
from src.schemas.vendor_types import VendorTypeOutSchema
from src.schemas.vendors import UpdateVendor, VendorInSchema, VendorOutSchema


async def save_vendor(vendor: UpdateVendor, user: Auth0User, vendor_id: str = None) -> VendorOutSchema:
    note = vendor.note
    del vendor.note
    vendor_dict = vendor.dict(exclude_unset=True)

    vendor_dict["account_id"] = user.app_metadata.get("account_id")
    if 'type' in vendor_dict:
        vendor_dict['type_id'] = vendor_dict['type']['id']
        del vendor_dict['type']

    if vendor_id:
        saved_vendor = await vendor_crud.update(
            user.app_metadata.get("account_id"), vendor_id, VendorInSchema(**vendor_dict)
        )
    else:
        saved_vendor = await vendor_crud.create(VendorInSchema(**vendor_dict))

    if note:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user.app_metadata["id"],
                vendor_id=saved_vendor.id,
            )
        )

    return saved_vendor


async def get_all_vendor_types(user: Auth0User) -> List[VendorTypeOutSchema]:
    return await vendor_type_crud.get_all(user.app_metadata.get("account_id"))


async def get_all_vendor(user: Auth0User) -> List[VendorOutSchema]:
    return await vendor_crud.get_all(user.app_metadata.get("account_id"))


async def get_vendor(vendor_id: str, user: Auth0User) -> VendorOutSchema:
    try:
        return await vendor_crud.get_one(user.app_metadata.get("account_id"), vendor_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")


async def create_vendor(vendor: UpdateVendor, user: Auth0User) -> VendorOutSchema:
    return await save_vendor(vendor, user)


async def update_vendor(vendor_id: str, vendor: UpdateVendor, user: Auth0User) -> VendorOutSchema:
    try:
        return await save_vendor(vendor, user, vendor_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")


async def delete_vendor(vendor_id: str, user: Auth0User) -> Status:
    res = await vendor_crud.delete_one(user.app_metadata.get("account_id"), vendor_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor does not exist")

    return Status(message="Deleted vendor")
