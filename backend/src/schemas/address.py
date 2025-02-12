# Python imports

# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.address import Address


class CreateUpdateAddress(BaseModel):
    city: Optional[str]
    county: Optional[str]
    state: Optional[str]
    street_address: Optional[str]
    zip: Optional[str]
    type: Optional[str]
    longitude: Optional[str]
    latitude: Optional[str]
    line_item_id: Optional[str]
    inventory_id: Optional[str]


class CreateAddress(BaseModel):
    city: Optional[str]
    county: Optional[str]
    state: Optional[str]
    street_address: Optional[str]
    zip: Optional[str]


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


AddressOut = pydantic_model_creator(
    Address, name="AddressOut", exclude=['modified_at', 'created_at'], config_class=Config
)

AddressIn = pydantic_model_creator(
    Address,
    name="AddressIn",
    exclude=["id", "created_at", "modified_at"],
    exclude_readonly=True,
    config_class=Config,
)
