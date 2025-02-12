
# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.country import Country


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

countryIn = pydantic_model_creator(
    Country,
    name="countryIn",
    exclude=("id", "created_at", "modified_at", "account_id"),
    exclude_readonly=True,
    config_class=Config,
)

countryOut = pydantic_model_creator(
    Country,
    name="countryOut",
    exclude_readonly=True
)
