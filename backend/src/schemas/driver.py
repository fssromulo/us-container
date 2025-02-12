# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.driver import Driver
from src.schemas.notes import UpdateNote


included_fields = (
    "company_name",
    "cost_per_mile",
    "cost_per_100_miles",
    "phone_number",
    "email",
    "city",
    "state",
    "account_id",
)


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


DriverInSchema = pydantic_model_creator(Driver, name="DriverIn", include=included_fields, config_class=Config)

DriverInSchemaUSAC = pydantic_model_creator(
    Driver,
    name="DriverInUSAC",
    exclude=(
        "created_at",
        "modified_at",
        "account",
        "deliveries",
        "line_item_driver",
        "line_item_driver_potential",
        "note",
    ),
)

DriverOutSchema = pydantic_model_creator(Driver, name="DriverOut")


class UpdateDriver(BaseModel):
    company_name: Optional[str]
    cost_per_mile: Optional[float]
    cost_per_100_miles: Optional[float]
    phone_number: Optional[str]
    email: Optional[str]
    city: Optional[str]
    state: Optional[str]
    province: Optional[str]
    note: Optional[UpdateNote]

    class Config:
        arbitrary_types_allowed = True
