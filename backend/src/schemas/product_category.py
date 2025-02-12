# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.pricing.product_category import ProductCategory


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


ProductCategoryIn = pydantic_model_creator(ProductCategory, name="ProductCategoryIn", exclude_readonly=True)

ProductCategoryOut = pydantic_model_creator(
    ProductCategory,
    name="ProductCategoryOut",
    exclude=("account", "line_items"),
)


class CreateUpdateProductCategory(BaseModel):
    name: Optional[str]
