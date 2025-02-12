# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.pricing.location_price import LocationPrice


include = ["id", "account_id", "city", "region", "state", "zip"]


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


LocationPriceIn = pydantic_model_creator(
    LocationPrice, name="LocationPriceIn", include=include, exclude_readonly=True, config_class=Config
)

LocationPriceOut = pydantic_model_creator(LocationPrice, name="LocationPriceOut", exclude=["fixed_location_prices"])
