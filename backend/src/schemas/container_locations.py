# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.container_types import ContainerTypes
from src.database.models.pricing.location_price import LocationPrice, PickupRegion
from src.database.models.pricing.region import Region


location_includes = [
    "id",
    "city",
    "cost_per_mile",
    "zip",
    "minimum_shipping_cost",
    "state",
    "region",
]


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


LocationPriceInSchema = pydantic_model_creator(
    LocationPrice, name="LocationPriceIn", exclude_readonly=True, config_class=Config
)

LocationPriceOutSchema = pydantic_model_creator(LocationPrice, name="LocationPriceOut")


class CreateUpdateLocationPrice(BaseModel):
    city: Optional[str]
    cost_per_mile: Optional[Decimal]
    zip: Optional[str]
    minimum_shipping_cost: Optional[Decimal]
    state: Optional[str]
    province: Optional[str]
    region: Optional[Region]
    pickup_region: Optional[PickupRegion]
    average_delivery_days: Optional[int]

    class Config:
        arbitrary_types_allowed = True


class CreateUpdateContainerPrice(BaseModel):
    container_size: Optional[str]
    product_type: Optional[ContainerTypes]
    price: Optional[Decimal]
    attributes: Optional[dict]
    condition: Optional[str]
    description: Optional[str]
    location_id: Optional[str]
    monthly_price: Optional[Decimal]
    cost_per_mile: Optional[Decimal]
    minimum_shipping_cost: Optional[Decimal]
    pod: Optional[bool]
    average_delivery_days: Optional[int]
