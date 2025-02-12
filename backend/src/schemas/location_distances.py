from typing import Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models.location_distance import LocationDistances

class CreateLocationDistances(BaseModel):
    destination_zip: Optional[str]
    destination_city: Optional[str]
    origin_zip: Optional[str]
    distance: Optional[Decimal]

    class Config:
        arbitrary_types_allowed = True

LocationDistancesIn = pydantic_model_creator(
    LocationDistances, name="LocationDistancesIn", exclude_readonly=True
)

LocationDistancesOut = pydantic_model_creator(
    LocationDistances, name="LocationDistancesOut"
)