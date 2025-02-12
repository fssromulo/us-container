# Python imports
# import logging
# import os
# import random

# Pip imports
# from fastapi import HTTPException, status
# from tortoise import Model
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.crud.address_crud import address_crud
from src.crud.inventory_address_crud import inventory_address_crud
from src.crud.line_item_crud import line_item_crud
from src.schemas.address import AddressIn, AddressOut, CreateUpdateAddress
from src.schemas.inventory_address import InventoryAddressIn, InventoryAddressOut
from src.schemas.line_items import LineItemOut


@atomic()
async def create_inventory_address(address: CreateUpdateAddress, user: Auth0User) -> LineItemOut:
    line_item_id = address.line_item_id
    inventory_id = address.inventory_id
    address_dict = address.dict()
    del address_dict['line_item_id']
    del address_dict['inventory_id']

    created_address_obj = await address_crud.create(AddressIn(**address_dict))

    inventory_address_dict = {}
    inventory_address_dict['line_item_id'] = line_item_id
    inventory_address_dict['inventory_id'] = inventory_id
    inventory_address_dict['address_id'] = created_address_obj.id

    res_model = await inventory_address_crud.create(InventoryAddressIn(**inventory_address_dict))

    line_item = await line_item_crud.get_one(user.app_metadata['account_id'], line_item_id)

    return line_item


@atomic()
async def update_inventory_address(id: str, address: CreateUpdateAddress, user: Auth0User) -> LineItemOut:
    address_dict = address.dict()
    del address_dict['line_item_id']
    del address_dict['inventory_id']

    await address_crud.updateWithoutRetrieval(user.app_metadata['account_id'], id, AddressIn(**address_dict))

    line_item = await line_item_crud.get_one(user.app_metadata['account_id'], address.line_item_id)

    return line_item
