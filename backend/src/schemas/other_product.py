# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.pricing.other_product import OtherProduct
from src.database.models.pricing.product_category import ProductCategory


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


OtherProductIn = pydantic_model_creator(OtherProduct, name="OtherProductIn", exclude_readonly=True)

OtherProductOut = pydantic_model_creator(OtherProduct, name="OtherProductOut")


class CreateUpdateOtherProduct(BaseModel):
    product_category: Optional[str]
    sale_price: Optional[Decimal]
    attributes: Optional[dict]
    condition: Optional[str]
    description: Optional[str]
    location_id: Optional[str]
    shipping_time: Optional[str]
    product_link: Optional[str]
    in_stock: Optional[bool]
    name: Optional[str]
    description: Optional[str]
    price: Optional[Decimal]
    minimum_shipping_cost: Optional[Decimal]
    product_category_id: Optional[str]
