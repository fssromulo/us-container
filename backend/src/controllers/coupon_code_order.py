# Python imports
from decimal import Decimal
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from tortoise.transactions import atomic

# Internal imports
from src.controllers import balance as balance_controller
from src.crud.account_crud import account_crud
from src.crud.coupon_code_crud import coupon_code_crud
from src.crud.coupon_code_order_crud import coupon_code_order_crud
from src.crud.order_crud import OrderCRUD
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.crud.user_crud import UserCRUD
from src.database.models.note import Note
from src.database.models.orders.coupon_code_order import CouponCodeOrder
from src.database.models.orders.order import Order
from src.schemas.coupon_code import CouponCodeOut
from src.schemas.coupon_code_order import CouponCodeOrderIn, CouponCodeOrderOut
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.orders import OrderInUpdate, OrderOut
from src.schemas.token import Status


order_crud = OrderCRUD()
user_crud = UserCRUD()

note_crud = TortoiseCRUD(schema=NoteOutSchema, create_schema=NoteInSchema, update_schema=UpdateNote, db_model=Note)


async def update_order(account_id, order_id, user_id):
    await order_crud.update(
        account_id,
        order_id,
        OrderInUpdate(**{"is_discount_applied": True, "account_id": account_id, "user_id": user_id}),
    )


@atomic()
async def apply_coupon(coupon_code_order: CouponCodeOrderIn, background_tasks: BackgroundTasks) -> CouponCodeOrderOut:
    existing_order: Order = await order_crud.get_one(coupon_code_order.order_id)
    coupon = await coupon_code_crud.get_one(existing_order.account_id, coupon_code_order.coupon_id)
    account = await account_crud.get_one(existing_order.account_id)

    if coupon.is_stackable:
        coupons_in_order = await coupon_code_order_crud.get_all_by_order_id(account.id, coupon_code_order.order_id)
        if len(coupons_in_order) > 0 and coupons_in_order[0].is_stackable == False:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unstackable coupon already exists"
            )
    else:
        coupons_in_order = await coupon_code_order_crud.get_all_by_order_id(account.id, coupon_code_order.order_id)
        if len(coupons_in_order) > 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot apply unstackable coupon."
            )

    saved_coupon_order = await coupon_code_order_crud.create(coupon_code_order)
    created_coupon_order = await coupon_code_order_crud.get_by_order_coupon_id(coupon_code_order.order_id, coupon_code_order.coupon_id)
    background_tasks.add_task(update_order, existing_order.account_id, existing_order.id, existing_order.user.id)

    if account.cms_attributes.get('automated_user', False):
        user = await user_crud.get_by_email(existing_order.account_id, account.cms_attributes.get('automated_user'))
        await note_crud.create(
            NoteInSchema(
                title="Applied Coupon To Order",
                content="Applied Coupon To Order : " + coupon.name,
                author_id=user.id,
                order_id=existing_order.id,
            )
        )

    change_amount = None

    # if coupon.percentage:
    #     change_amount = (
    #         Decimal(existing_order.total_price)
    #         * Decimal(coupon.percentage)
    #         / Decimal(100)
    #         / Decimal(existing_order.line_item_length)
    #     )
    # else:
    #     change_amount = coupon.amount

    await balance_controller.line_item_discounted_revenue_adjustment(
        existing_order, False, coupon.id, created_coupon_order.id
    )
    return saved_coupon_order


async def background_task(order_id):
    existing_order: Order = await order_crud.get_one(order_id, True)
    if len(existing_order.coupon_code_order) == 0:
        await order_crud.update(
            existing_order.account_id,
            order_id,
            OrderInUpdate(
                **{
                    "is_discount_applied": False,
                    "account_id": existing_order.account_id,
                    "user_id": existing_order.user.id,
                }
            ),
        )


@atomic()
async def remove_coupon(coupon_code_order: CouponCodeOrderIn, background_tasks: BackgroundTasks) -> None:
    existing_order: Order = await order_crud.get_one(coupon_code_order.order_id)
    coupon = await coupon_code_crud.get_one(existing_order.account_id, coupon_code_order.coupon_id)
    existing_coupon_order = await coupon_code_order_crud.get_by_order_coupon_id(coupon_code_order.order_id, coupon_code_order.coupon_id)

    await coupon_code_order_crud.delete_one_by_coupon_id_and_order_id(
        coupon_code_order.order_id, coupon_code_order.coupon_id
    )
    account = await account_crud.get_one(existing_order.account_id)

    background_tasks.add_task(background_task, coupon_code_order.order_id)
    if account.cms_attributes.get('automated_user', False):
        user = await user_crud.get_by_email(existing_order.account_id, account.cms_attributes.get('automated_user'))
        await note_crud.create(
            NoteInSchema(
                title="Removed Coupon From Order",
                content="Removed Coupon From : " + coupon.name,
                author_id=user.id,
                order_id=existing_order.id,
            )
        )

    # asmount_change = None
    # if coupon.percentage:
    #     asmount_change = (
    #         Decimal(existing_order.total_price)
    #         * Decimal(coupon.percentage)coupon_code_order
    #         / Decimal(100)
    #         / Decimal(existing_order.line_item_length)
    #     )
    # else:
    #     asmount_change = coupon.amount

    # await balance_controller.line_item_revenue_adjustment(
    #     existing_order, asmount_change, True, coupon.minimum_discount_threshold
    # )
    await balance_controller.line_item_discounted_revenue_adjustment(
        existing_order, True, coupon.id, existing_coupon_order.id
    )
    return Status(message="Removed applied coupon code")


async def get_all_applied_coupons(account_id, order_id: str) -> List[CouponCodeOut]:
    return await coupon_code_order_crud.get_all_by_order_id(account_id, order_id)


async def get_all_orders(coupon_code_id: str) -> List[OrderOut]:
    return await coupon_code_order_crud.get_all_by_coupon_code_id(coupon_code_id)


@atomic()
async def unset_coupon(coupon_code_order_id: str) -> Status:
    coupon_code_order: CouponCodeOrder = await coupon_code_order_crud.get_one_by_id(coupon_code_order_id)
    existing_order: Order = await order_crud.get_one(coupon_code_order.order_id, True)
    coupon = await coupon_code_crud.get_one(existing_order.account_id, coupon_code_order.coupon_id)

    await balance_controller.line_item_revenue_adjustment(
        existing_order, coupon.amount, True, coupon.minimum_discount_threshold
    )
    await coupon_code_order_crud.delete_by_id(coupon_code_order_id)

    existing_order: Order = await order_crud.get_one(coupon_code_order.order_id, True)
    if len(existing_order.coupon_code_order) == 0:
        await order_crud.update(
            existing_order.account_id,
            coupon_code_order.order_id,
            OrderInUpdate(
                **{
                    "is_discount_applied": False,
                    "account_id": existing_order.account_id,
                    "user_id": existing_order.user.id,
                }
            ),
        )
    return Status(message="Removed attached coupon code")


async def unset_mass_coupons(coupon_code_id: str, ids: list[str]) -> Status:
    await Order.filter(id__in=ids).update(is_discount_applied=False)
    await coupon_code_order_crud.delete_by_ids(coupon_code_id, ids)
    return Status(message="Removed attached coupon code")
