# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.other_inventory import OtherInventory


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


included_fields = [
    "id",
    "total_cost",
    "condition",
    "other_number",
    "other_release_number",
    "status",
    "purchase_type",
    "vendor_id",
    "account_id",
    "type",
    "invoice_number",
    "purchased_at",
    "pickup_at",
    "payment_type",
    "surcharge_fee",
    "product_id",
]

OtherInventoryIn = pydantic_model_creator(
    OtherInventory, optional=included_fields, exclude_readonly=True, name="OtherInventoryIn", config_class=Config
)

OtherInventoryUpdateIn = pydantic_model_creator(
    OtherInventory,
    include=included_fields[1:],
    exclude_readonly=True,
    name="OtherInventoryUpdateIn",
    config_class=Config,
)

OtherInventoryOut = pydantic_model_creator(OtherInventory, name="OtherInventoryOut")
