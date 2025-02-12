# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.vendor import Vendor
from src.schemas.notes import UpdateNote


included_fields = [
    "id",
    "name",
    "address",
    "city",
    "state",
    "zip",
    "primary_phone",
    "primary_email",
    "secondary_phone",
    "secondary_email",
    "note",
]


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


VendorInSchema = pydantic_model_creator(
    Vendor, name="VendorIn", exclude=("id",), exclude_readonly=True, config_class=Config
)

VendorOutSchema = pydantic_model_creator(Vendor, name="VendorOut", exclude=("account_id",))


class VendorType(BaseModel):
    id: Optional[int]
    type: Optional[str]


class UpdateVendor(BaseModel):
    name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    primary_phone: Optional[str]
    primary_email: Optional[str]
    secondary_phone: Optional[str]
    secondary_email: Optional[str]
    note: Optional[UpdateNote]
    country: Optional[str]
    country_code_primary: Optional[str]
    country_code_secondary: Optional[str]
    type: Optional[VendorType]

    class Config:
        arbitrary_types_allowed = True
