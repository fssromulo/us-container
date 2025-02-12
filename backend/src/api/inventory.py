# Python imports
import os
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi_cache import FastAPICache, default_key_builder
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import inventory, other_inventory
from src.crud._types import PAGINATION
from src.crud.container_inventory_crud import container_inventory_crud
from src.dependencies import auth
from src.schemas.container_inventory import ContainerInventoryOut
from src.schemas.inventory import CreateOtherInventory, CreateUpdateInventory
from src.schemas.token import Status


BASE_WEB_URL = os.getenv("BASE_WEB_URL")
BASE_INVOICE_URL = os.getenv("BASE_INVOICE_URL")

router = APIRouter(
    tags=["inventory"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get(
    "/inventory_by_status",
    response_model=List[ContainerInventoryOut],
)
@cache(namespace="inventory",key_builder=default_key_builder, expire=60 * 10)
async def get_inventory_by_status(
    status: str,
    order_type: str,
    pagination: PAGINATION = container_inventory_crud.pagination_depends,
    user: Auth0User = Depends(auth.get_user),
):
    if pagination['limit'] == 1:
        pagination['limit'] = 50
    return await inventory.get_inventory_by_status(status, order_type, pagination, user)


@router.get(
    "/search_inventory",
)
async def search_inventory(
    searchBy: str = None,
    searchValue: str = None,
    searchStatus: str = None,
    user: Auth0User = Depends(auth.get_user),
):
    return await inventory.search_inventory(user, searchBy, searchValue, searchStatus)


@router.get("/get_order_for_container")
async def get_order_for_container(
    container_id: str,
    user: Auth0User = Depends(auth.get_user),
):
    return await inventory.get_order_by_container_id(container_id)


@router.get(
    "/inventory_by_depot/{depot_id}",
    response_model=List[ContainerInventoryOut],
)
async def get_inventory_by_depot(depot_id: str, user: Auth0User = Depends(auth.get_user)):
    return await inventory.get_inventory_by_depot(depot_id, user)


@router.get(
    "/inventory/{id}",
    response_model=ContainerInventoryOut,
)
async def get_container_inventory(id: str, user: Auth0User = Depends(auth.get_user)):
    return await inventory.get_container_inventory(id, user)


@router.get(
    "/inventory/prefix/{id}",
    response_model=ContainerInventoryOut,
)
async def get_container_inventory_prefix(id: str, user: Auth0User = Depends(auth.get_user)):
    if len([p for p in user.permissions if p == "read:inventory-containers"]) != 0:
        return await inventory.get_container_inventory_prefix(id, user)
    return None


@router.get("/related_containers")
async def get_related_container_inventory(release_number: str, user: Auth0User = Depends(auth.get_user)):
    # if len([p for p in user.permissions if p == "read:inventory-containers"]) != 0:
    return await inventory.fetch_related_containers(release_number, user)
    return None


@router.post(
    "/inventory",
    response_model=List[ContainerInventoryOut],
)
async def create_inventory(inventoryCreateUpdate: CreateUpdateInventory, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    # delete_line_item = [p for p in user.permissions if p == "create:inventory-containers"]
    # if not delete_line_item:
    #   raise HTTPException(
    #       status_code=status.HTTP_403_FORBIDDEN,
    #       detail="You do not have permission to save a container",
    #     )
    await FastAPICache.clear(namespace="inventory")

    return await inventory.create_inventory(inventoryCreateUpdate, user, background_tasks=background_tasks)


@router.post(
    "/other_inventory",
)
async def create_other_inventory(
    inventoryCreateUpdate: CreateOtherInventory,
    backgroundTasks: BackgroundTasks,
    user: Auth0User = Depends(auth.get_user),
):
    return await other_inventory.create_other_inventory(inventoryCreateUpdate, user, backgroundTasks)


@router.patch(
    "/other_inventory/{id}",
)
async def update_other_inventory(
    id: str,
    inventoryCreateUpdate: CreateOtherInventory,
    backgroundTasks: BackgroundTasks,
    user: Auth0User = Depends(auth.get_user),
):
    return await other_inventory.update_other_inventory(id, inventoryCreateUpdate, user, backgroundTasks)


@router.delete(
    "/other_inventory/{id}",
)
async def detach_other_inventory(id: str, backgroundTasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await other_inventory.detach_other_inventory(id, user, backgroundTasks)


@router.patch(
    "/inventory/{id}",
    response_model=ContainerInventoryOut,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_inventory(
    id: str, inventoryCreateUpdate: CreateUpdateInventory, user: Auth0User = Depends(auth.get_user)
):
    # delete_line_item = [p for p in user.permissions if p == "update:inventory-containers"]
    # if not delete_line_item:
    #   raise HTTPException(
    #       status_code=status.HTTP_403_FORBIDDEN,
    #       detail="You do not have permission to update a container",
    #     )
    await FastAPICache.clear(namespace="inventory")

    return await inventory.update_inventory(id, inventoryCreateUpdate, user)


@router.delete(
    "/inventory/{id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
)
async def delete_container_inventory(
    id: str, backgroundTasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
):
    await FastAPICache.clear(namespace="inventory")

    return await inventory.delete_container_inventory(id, user, backgroundTasks)
