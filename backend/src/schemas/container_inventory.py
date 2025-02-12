# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.container_inventory import ContainerInventory


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


included_fields = [
    "id",
    "total_cost",
    "condition",
    "container_number",
    "container_release_number",
    "status",
    "container_size",
    "purchase_type",
    "vendor_id",
    "account_id",
    "type",
    "invoice_number",
    "purchased_at",
    "pickup_at",
    "payment_type",
    "surcharge_fee",
    "high_cube",
    "double_door",
    "standard",
    "height",
    "width",
    "length",
    "product_id",
]

ContainerInventoryIn = pydantic_model_creator(
    ContainerInventory, include=included_fields, exclude_readonly=True, name="ContainerInventoryIn", config_class=Config
)

ContainerInventoryUpdateIn = pydantic_model_creator(
    ContainerInventory,
    include=included_fields[1:],
    exclude_readonly=True,
    name="ContainerInventoryUpdateIn",
    config_class=Config,
)

ContainerInventoryOut = pydantic_model_creator(ContainerInventory, name="ContainerInventoryOut")
