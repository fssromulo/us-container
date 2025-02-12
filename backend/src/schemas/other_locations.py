# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.other_types import OtherTypes
from src.database.models.pricing.location_price import LocationPrice
from src.database.models.pricing.other_product import OtherProduct
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
    region: Optional[Region]

    class Config:
        arbitrary_types_allowed = True
