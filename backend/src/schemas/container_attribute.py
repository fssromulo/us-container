# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.container_attribute import ContainerAttribute


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


ContainerAttributeIn = pydantic_model_creator(
    ContainerAttribute, name="ContainerAttributeIn", exclude=(), exclude_readonly=True, config_class=Config
)

ContainerAttributeOut = pydantic_model_creator(ContainerAttribute, name="ContainerAttributeOut")
