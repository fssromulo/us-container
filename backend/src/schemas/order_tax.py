
# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_tax import OrderTax


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

OrderTaxIn = pydantic_model_creator(
    OrderTax,
    name="OrderTaxIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

OrderTaxOut = pydantic_model_creator(
    OrderTax,
    name="OrderTaxOut",
    exclude_readonly=True
)
