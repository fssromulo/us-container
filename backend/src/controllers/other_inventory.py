# Python imports
import logging
import os
import uuid
from typing import Dict

# Pip imports
from fastapi import BackgroundTasks, HTTPException, status
from tortoise import Model
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud._types import PAGINATION
from src.crud.line_item_crud import line_item_crud
from src.schemas.inventory import CreateOtherInventory
from src.schemas.other_inventory import OtherInventoryIn, OtherInventoryOut, OtherInventoryUpdateIn
from src.schemas.token import Status
from src.services.notifications.email_service import send_tracking_number, send_tracking_number_attached

from ..crud.order_crud import OrderCRUD
from ..crud.other_inventory_crud import other_inventory_crud


order_crud = OrderCRUD()


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND)


async def create_other_inventory(inventory: CreateOtherInventory, user: Auth0User, backgroundTasks: BackgroundTasks):
    # Save new inventory
    other_inventory = await other_inventory_crud.create(
        OtherInventoryIn(
            **{
                "id": str(uuid.uuid4()),
                "account_id": user.app_metadata["account_id"],
                "vendor_id": inventory.vendor_id,
                "delivered": inventory.delivered,
                "quantity": inventory.quantity,
                "tracking_number": inventory.tracking_number,
                "product_id": inventory.product_id,
                "price": inventory.price,
                "total_cost": inventory.cost,
                "status": "Attached",
                "invoice_number": inventory.invoice_number,
            }
        ),
    )
    result = await line_item_crud.db_model.filter(id=inventory.line_item_id).update(
        other_inventory_id=other_inventory.id
    )

    line_item = await line_item_crud.get_one(user.app_metadata["account_id"], inventory.line_item_id)
    order = await order_crud.get_one(line_item.order.id)

    all_line_items_set = True
    for line_item in order.line_items:
        if line_item.product_type == 'CONTAINER_ACCESSORY':
            if not line_item.other_inventory:
                all_line_items_set = False

    if all_line_items_set:
        # permissions = len([p for p in user.permissions if p == "send:accessory_emails"])
        # if permissions != 0:
        send_tracking_number_attached(order)

    # send_tracking_number(order.dict(), inventory.tracking_number)
    return result


async def update_other_inventory(
    id: str, inventory: CreateOtherInventory, user: Auth0User, backgroundTasks: BackgroundTasks
):
    # Save new inventory
    await other_inventory_crud.update(
        user.app_metadata["account_id"],
        id,
        OtherInventoryIn(
            **{
                "vendor_id": inventory.vendor_id,
                "delivered": inventory.delivered,
                "quantity": inventory.quantity,
                "tracking_number": inventory.tracking_number,
            }
        ),
    )
    pass


async def detach_other_inventory(id: str, user: Auth0User, backgroundTasks: BackgroundTasks):
    # Save new inventory
    other_inventory = await other_inventory_crud.update(
        user.app_metadata["account_id"],
        id,
        OtherInventoryIn(
            **{
                "status": "Available",
            }
        ),
    )
    return await line_item_crud.db_model.filter(other_inventory_id=id).update(other_inventory_id=None)
