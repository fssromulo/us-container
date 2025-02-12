# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory_address import InventoryAddress


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


InventoryAddressIn = pydantic_model_creator(
    InventoryAddress,
    name="InventoryAddressIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

InventoryAddressOut = pydantic_model_creator(InventoryAddress, name="InventoryAddressOut", exclude_readonly=True)
