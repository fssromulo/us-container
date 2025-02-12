# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import coupon_code as coupon_controller
from src.controllers import coupon_code_order as coupon_order_controller
from src.dependencies import auth
from src.schemas.coupon_code import CouponCodeIn, CouponCodeMassDelete, CouponCodeOut, CouponCodeUpdate
from src.schemas.coupon_code_order import CouponCodeOrderIn, CouponCodeOrderOut
from src.schemas.orders import OrderOut
from src.schemas.token import Status


router = APIRouter(
    tags=["coupon"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/coupons", response_model=List[CouponCodeOut])
@cache(namespace="coupon_code", expire=60 * 10)
async def get_coupons(user: Auth0User = Depends(auth.get_user)):
    return await coupon_controller.get_all_coupons(user)


@router.get("/coupon/{coupon_code_id}", response_model=CouponCodeOut)
async def get_coupon_by_id(coupon_code_id: str, user: Auth0User = Depends(auth.get_user)) -> CouponCodeOut:
    return await coupon_controller.get_coupon(coupon_code_id, user)


@router.get("/coupon/code/{coupon_code}", response_model=CouponCodeOut)
async def get_coupon_by_code(coupon_code: str, user: Auth0User = Depends(auth.get_user)) -> CouponCodeOut:
    return await coupon_controller.get_coupon_by_code(coupon_code, user)


@router.post("/coupon", response_model=CouponCodeOut)
async def create_coupon(coupon: CouponCodeIn, user: Auth0User = Depends(auth.get_user)) -> CouponCodeOut:
    await FastAPICache.clear(namespace="coupon_code")
    return await coupon_controller.create_coupon(coupon, user)


@router.patch("/coupon/{coupon_code_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def update_coupon(
    coupon_code_id: str, coupon: CouponCodeUpdate, user: Auth0User = Depends(auth.get_user)
) -> Status:
    await FastAPICache.clear(namespace="coupon_code")
    return await coupon_controller.update_coupon(coupon_code_id, coupon, user)


@router.delete("/coupon/{coupon_code_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_coupon(coupon_code_id: str):
    return await coupon_controller.delete_coupon(coupon_code_id)


# Coupon Code Orders
@router.post("/coupon/apply", response_model=CouponCodeOrderOut, responses={404: {"model": HTTPNotFoundError}})
async def apply_coupon(coupon: CouponCodeOrderIn, background_tasks: BackgroundTasks) -> CouponCodeOrderOut:
    return await coupon_order_controller.apply_coupon(coupon, background_tasks)


@router.post("/coupon/remove", responses={404: {"model": HTTPNotFoundError}})
async def remove_coupon(coupon: CouponCodeOrderIn, background_tasks: BackgroundTasks) -> None:
    return await coupon_order_controller.remove_coupon(coupon, background_tasks)


@router.get("/coupon/orders/{coupon_code_id}", response_model=List[OrderOut])
async def get_linked_orders(coupon_code_id: str):
    return await coupon_order_controller.get_all_orders(coupon_code_id)


@router.get("/coupon/codes/{order_id}", response_model=List[CouponCodeOut])
async def get_linked_coupons(order_id: str, user: Auth0User = Depends(auth.get_user)):
    return await coupon_order_controller.get_all_applied_coupons(user.app_metadata['account_id'], order_id)


@router.delete(
    "/coupon/unset/{coupon_code_order_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def unset_coupon(coupon_code_order_id: str) -> Status:
    return await coupon_order_controller.unset_coupon(coupon_code_order_id)


@router.delete(
    "/coupon/unset-all/{coupon_code_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}
)
async def unset_all(coupon_code_id: str, delete_data: CouponCodeMassDelete) -> Status:
    return await coupon_order_controller.unset_mass_coupons(coupon_code_id, delete_data.ids)
