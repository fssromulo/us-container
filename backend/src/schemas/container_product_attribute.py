# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.container_product_attribute import ContainerProductAttribute


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


ContainerProductAttributeIn = pydantic_model_creator(
    ContainerProductAttribute,
    name="ContainerProductAttributeIn",
    exclude=(),
    exclude_readonly=True,
    config_class=Config,
)

ContainerProductAttributeOut = pydantic_model_creator(ContainerProductAttribute, name="ContainerProductAttributeOut")
