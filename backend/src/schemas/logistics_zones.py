# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.logistics_zones import LogisticsZones


LogisticsZonesInSchema = pydantic_model_creator(LogisticsZones, name="LogisticsZonesIn", exclude_readonly=True)

LogisticsZonesOutSchema = pydantic_model_creator(LogisticsZones, name="LogisticsZonesOut")


class CreateUpdateLogisticsZone(BaseModel):
    zone_name: Optional[str]
    coordinator_name: Optional[str]
    email: Optional[str]
    direct_number: Optional[str]
    support_number: Optional[str]
    color: Optional[str]
