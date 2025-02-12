# Python imports
import logging
import os
import uuid
from typing import Dict
import json

# Pip imports
from fastapi import BackgroundTasks, HTTPException, status
from tortoise import Model
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.controllers.event_controller import send_event
from src.crud._types import PAGINATION
from src.schemas.container_inventory import ContainerInventoryIn, ContainerInventoryUpdateIn
from src.schemas.inventory import CreateUpdateInventory
from src.schemas.token import Status
from src.utils.utility import make_json_serializable

from ..crud.container_inventory_crud import container_inventory_crud
from ..crud.order_crud import OrderCRUD
from ..crud.other_inventory_crud import other_inventory_crud
from src.controllers.event_controller import inventory_created, inventory_updated, inventory_deleted

order_crud = OrderCRUD()


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND)


async def get_container_inventorys(user: Auth0User, pagination: PAGINATION) -> Model:
    return await container_inventory_crud.get_all(user.app_metadata["account_id"], pagination)


async def get_other_inventorys(user: Auth0User, pagination: PAGINATION) -> Model:
    return await other_inventory_crud.get_all(user.app_metadata["account_id"], pagination)


def inventory_to_order(inventory):
    if not inventory:
        return None
    return {
        "display_order_id": None,
        "line_items": [
            {
                "potential_date": None,
                "scheduled_date": None,
                "status": inventory.status,
                "inventory": inventory,
            }
        ],
    }


async def convert_search_to_order(account_id, searchBy, searchValue, searchStatus):
    if searchBy == "CONTAINER_RELEASE":
        found_inventory = await container_inventory_crud.search_inventory(
            account_id, container_release=searchValue, container_availability=searchStatus
        )
    if searchBy == "CONTAINER_NUMBER":
        found_inventory = await container_inventory_crud.search_inventory(
            account_id, container_number=searchValue, container_availability=searchStatus
        )
    response_list = []
    found_orders = await order_crud.get_by_inventory_ids([i.id for i in found_inventory])
    found_order_inventory_ids = [
        [str(i.inventory.id) for i in order.line_items if i.inventory] for order in found_orders
    ]
    found_order_inventory_ids = [item for sublist in found_order_inventory_ids for item in sublist]
    missing_inventory = [i for i in found_inventory if i.id not in found_order_inventory_ids]
    for inventory in missing_inventory:
        response_list.append(inventory_to_order(inventory))
    response_list.extend(found_orders)
    return response_list


async def search_inventory(
    user: Auth0User,
    searchBy: str = None,
    searchValue: str = None,
    searchStatus: str = None,
):
    if searchBy == "ORDER_ID":
        order = await order_crud.get_one_by_display_id(user.app_metadata["account_id"], searchValue)
        return [order]
    return await convert_search_to_order(user.app_metadata["account_id"], searchBy, searchValue, searchStatus)


async def get_order_by_container_id(container_id: str):
    return await order_crud.get_order_by_container_id(container_id)


async def get_order_by_other_id(other_id: str):
    return await order_crud.get_order_by_container_id(other_id)


async def get_inventory_by_status(
    status: str,
    order_type: str,
    pagination: PAGINATION,
    user: Auth0User,
):
    if user.app_metadata["account_id"] == 1:
        order_type = None
    return await container_inventory_crud.get_by_status_type(
        user.app_metadata["account_id"], status, order_type, pagination
    )


async def get_inventory_by_depot(depot_id: str, user: Auth0User):
    return await container_inventory_crud.get_inventory_by_depot(user.app_metadata["account_id"], depot_id)


async def fetch_related_containers(release_number: str, user: Auth0User):
    return await container_inventory_crud.search_related_inventory(user.app_metadata["account_id"], release_number)


async def get_container_inventory_prefix(id: str, user: Auth0User):
    try:
        return await container_inventory_crud.get_one_prefix(user.app_metadata["account_id"], id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Container inventory does not exist",
        )


async def get_container_inventory(id: str, user: Auth0User):
    try:
        result = await container_inventory_crud.get_one(user.app_metadata["account_id"], id)
        for rh in result.rental_history:
            order_id = rh.line_item.order.id
            order = await order_crud.get_one(order_id)
            setattr(rh.line_item.order, "calculated_paid_thru", order.calculated_paid_thru)
        return result
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Container inventory does not exist",
        )


async def update_container_inventory_dict(account_id, inventory_id, inventory_dict):
    inventory_dict['account_id'] = account_id
    saved_container = await container_inventory_crud.update(
        account_id,
        inventory_id,
        ContainerInventoryUpdateIn(**inventory_dict),
    )
    return saved_container


async def check_if_inventory_matches(account_id, inventory_id, line_item):
    container = await container_inventory_crud.get_one(account_id, inventory_id)

    if container.product:
        if str(container.product.container_size) != str(line_item.container_size) or str(
            container.product.condition
        ) != str(line_item.condition):
            return False

        attributes_in_inventory = {}
        for cpa in container.product.container_product_attributes:
            name = cpa.container_attribute.name
            if name == 'Standard':
                attributes_in_inventory['standard'] = True
            if name == 'High Cube':
                attributes_in_inventory['high_cube'] = True
            if name == 'Double Door':
                attributes_in_inventory['double_door'] = True

        for attribute in attributes_in_inventory:
            if attributes_in_inventory[attribute] != line_item.attributes.get(attribute, False):
                return False

    return True


def process_dimensions(item) -> Dict[str, str]:
    if not item:
        item = "0x0x0"
    dimensions = item.split("x")

    return {"length": str(dimensions[0]), "width": str(dimensions[1]), "height": str(dimensions[2])}


async def save_new_inventory(inventory: CreateUpdateInventory, user, inventory_id=None):
    if inventory.container_number:
        found_container = await container_inventory_crud.get_one_container_number(
            user.app_metadata["account_id"], inventory.container_number
        )
        if (found_container and inventory_id is None) or (found_container and inventory_id != found_container.id):
            raise HTTPException("Container number already used")

    if not inventory.image_urls:
        inventory.image_urls = []

    if inventory_id is None:
        container_inventory_id = str(uuid.uuid4())
        result = await container_inventory_crud.create(
            ContainerInventoryIn(
                **{
                    "id": container_inventory_id,
                    "total_cost": inventory.total_cost,
                    "purchase_type": inventory.purchase_type,
                    "invoice_number": inventory.invoice_number,
                    "paid_at": inventory.paid_at,
                    "invoiced_at": inventory.invoiced_at,
                    "pickup_at": inventory.pickup_at,
                    "payment_type": inventory.payment_type,
                    "container_number": inventory.container_number,
                    "container_release_number": inventory.container_release_number,
                    "product_id": inventory.product_id,
                    "vendor_id": inventory.vendor_id,
                    "depot_id": inventory.depot_id,
                    "account_id": user.app_metadata["account_id"],
                    "status": inventory.status if inventory.status else "Available",
                    "container_color": inventory.container_color,
                    "image_urls": json.dumps(inventory.image_urls),
                    "description": inventory.description,
                    "revenue": inventory.revenue
                }
            ),
        )
        metadata = await inventory_created(user.app_metadata['account_id'], result)
        if "woocomerce" in metadata and metadata['woocomerce'] == None:
            raise Exception("Woocomerce object wasn't created.")

        await container_inventory_crud.update(
                user.app_metadata["account_id"],
                container_inventory_id,
                ContainerInventoryUpdateIn(**{"metadata": metadata, "account_id": user.app_metadata['account_id']}),
            )
        return result
    else:
        result = await container_inventory_crud.get_one(user.app_metadata['account_id'], inventory_id)
        if result:
            update_dict = {
                "total_cost": inventory.total_cost,
                "status": inventory.status,
                "purchase_type": inventory.purchase_type,
                "invoice_number": inventory.invoice_number,
                "paid_at": inventory.paid_at,
                "invoiced_at": inventory.invoiced_at,
                "pickup_at": inventory.pickup_at,
                "payment_type": inventory.payment_type,
                "container_number": inventory.container_number,
                "container_release_number": inventory.container_release_number,
                "product_id": inventory.product_id,
                "vendor_id": inventory.vendor_id,
                "depot_id": inventory.depot_id,
                "account_id": user.app_metadata["account_id"],
                "container_color": inventory.container_color,
                "image_urls": json.dumps(inventory.image_urls),
                "description": inventory.description,
                "revenue": inventory.revenue
            }
            update_dict = {key: value for key, value in update_dict.items() if value is not None}

            result = await container_inventory_crud.update(
                user.app_metadata["account_id"],
                inventory_id,
                ContainerInventoryUpdateIn(**update_dict),
            )

            await inventory_updated(user.app_metadata['account_id'], result)

            return result
        raise NOT_FOUND


async def create_new_inventory(quantity: int, inventory: CreateUpdateInventory, user: Auth0User):
    list_of_results = []
    for q in range(quantity):
        list_of_results.append(await save_new_inventory(inventory, user, None))
    return list_of_results


async def update_new_inventory(inventory: CreateUpdateInventory, user: Auth0User, id: str):
    return await save_new_inventory(inventory, user, id)


async def delete_new_inventory(user: Auth0User, id: str):
    result = await container_inventory_crud.get_one(user.app_metadata['account_id'], id)
    if result:
        await inventory_deleted(user.app_metadata['account_id'], result)
        return await container_inventory_crud.delete_one(user.app_metadata['account_id'], id)
    else:
        return None


async def create_inventory(inventory: CreateUpdateInventory, user: Auth0User, background_tasks: BackgroundTasks):
    # inventory.purchase_type = "ALL"
    list_of_results = await create_new_inventory(inventory.quantity, inventory, user)
    # send event to event controller
    for result in list_of_results:
        background_tasks.add_task(
            send_event,
            user.app_metadata['account_id'],
            str(result.id),
            make_json_serializable(result.dict()),
            "inventory",
            "create",
        )
    return list_of_results


async def update_inventory(id: str, inventoryCreateUpdate: CreateUpdateInventory, user: Auth0User):
    return await update_new_inventory(inventoryCreateUpdate, user, id)


async def delete_container_inventory(id: str, user: Auth0User, backgroundTasks: BackgroundTasks):
    await delete_new_inventory(user, id)
    return Status(message="Container deleted")
