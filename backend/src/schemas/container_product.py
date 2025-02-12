# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional
from typing import List, Any

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.pricing.container_product import ContainerProduct


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


ContainerProductIn = pydantic_model_creator(
    ContainerProduct, name="ContainerProductIn", exclude_readonly=True, config_class=Config
)

ContainerProductOut = pydantic_model_creator(ContainerProduct, name="ContainerProductOut", config_class=Config)

class GlobalPodSettings(BaseModel):
    types: List[Any]
    condition: str 
    state: bool
    locations: List[str]

class IsPayOnDeliveryRequest(BaseModel):
    product_name: str
    location_name: str