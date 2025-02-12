# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.tax import Tax


included_fields = [
    "rate",
    "state",
]

TaxInSchema = pydantic_model_creator(Tax, name="TaxIn", exclude_readonly=True)

TaxOutSchema = pydantic_model_creator(Tax, name="TaxOut")


class CreateOrUpdateTax(BaseModel):
    rate: str
    state: str


class AvalaraTaxItem(BaseModel):
    customer_zip: str
    container_city: str
    container_state: str
