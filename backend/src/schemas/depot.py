# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.depot import Depot
from src.schemas.notes import UpdateNote


included_fields = [
    "id",
    "name",
    "street_address",
    "zip",
    "primary_email",
    "secondary_email",
    "primary_phone",
    "secondary_phone",
    "city",
    "state",
    "notes",
]


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


DepotInSchema = pydantic_model_creator(
    Depot,
    name="DepotIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

DepotInSchemaUSAC = pydantic_model_creator(
    Depot,
    name="DepotInUSAC",
    exclude=("created_at", "modified_at", "note", "account", "inventory"),
)

DepotOutSchema = pydantic_model_creator(Depot, name="DepotOut")


class CreateOrUpdateDepot(BaseModel):
    name: Optional[str]
    street_address: Optional[str]
    zip: Optional[str]
    primary_email: Optional[str]
    secondary_email: Optional[str]
    primary_phone: Optional[str]
    secondary_phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    note: Optional[UpdateNote]
