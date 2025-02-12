# Python imports
from typing import Optional
from typing import List, Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.fixed_location_price import FixedLocationPrice


FixedLocationPriceInSchema = pydantic_model_creator(FixedLocationPrice, name="FixedLocationPriceIn", exclude_readonly=True)

FixedLocationPriceOutSchema = pydantic_model_creator(
    FixedLocationPrice,
    name="FixedLocationPriceOut",
)
