# Python imports
from typing import List
from tortoise.exceptions import DoesNotExist
from fastapi import HTTPException, status

# Internal imports
from src.auth.auth import Auth0User
from src.crud.coupon_code_crud import coupon_code_crud
from src.schemas.coupon_code import CouponCodeIn, CouponCodeOut, CouponCodeUpdate, CouponCodeInsecureOut
from src.schemas.token import Status


async def save_coupon(coupon_code: CouponCodeIn, coupon_code_id: str = None, user: Auth0User = None) -> CouponCodeOut:
    coupon_code_dict = coupon_code.dict(exclude_unset=True)

    if coupon_code_id:
        saved_coupon = await coupon_code_crud.update(user.app_metadata.get("account_id"), coupon_code_id, CouponCodeIn(**coupon_code_dict))
    else:
        saved_coupon = await coupon_code_crud.create(CouponCodeIn(**coupon_code_dict))
    return saved_coupon


async def get_all_coupons_insecure(account_id) -> List[CouponCodeInsecureOut]:
    response = await coupon_code_crud.get_all(account_id)
    lst = []
    for coupon in response:
        dictionary = coupon.dict()
        del dictionary['code']
        del dictionary['id']
        lst.append(CouponCodeInsecureOut(**dictionary))
    return lst

async def get_all_coupons(user: Auth0User) -> List[CouponCodeOut]:
    return await coupon_code_crud.get_all(user.app_metadata.get("account_id"))

async def get_coupon(coupon_code_id: str, user: Auth0User) -> CouponCodeOut:
    try:
        return await coupon_code_crud.get_one(user.app_metadata.get("account_id"), coupon_code_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon does not exist")

async def get_coupon_by_code(coupon_code: str, user: Auth0User) -> CouponCodeInsecureOut:
    return await coupon_code_crud.get_one_by_code(coupon_code, user.app_metadata.get("account_id"))

async def get_public_coupon_by_code(coupon_code: str, account_id: int) -> CouponCodeInsecureOut:
    return await coupon_code_crud.get_one_by_code(coupon_code, account_id)

async def create_coupon(coupon_code: CouponCodeIn, user: Auth0User) -> CouponCodeOut:
    coupon_code.account_id = user.app_metadata.get("account_id")
    return await coupon_code_crud.create(coupon_code)


async def update_coupon(coupon_code_id: str, coupon: CouponCodeUpdate, user: Auth0User) -> Status:
    await coupon_code_crud.update(user.app_metadata.get("account_id"), coupon_code_id, coupon)
    return Status(message=f"Coupon has been updated")

async def delete_coupon(coupon_code_id: str)-> Status:
    await coupon_code_crud.delete_by_id(coupon_code_id)
    return Status(message=f"Removed attached coupon code")


