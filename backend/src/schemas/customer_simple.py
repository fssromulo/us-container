# Python imports

# Python imports
from typing import List, Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.customer.old_customer import Customer


class CreateCustomer(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    customer_contacts: Optional[List[dict]]
    company_name: Optional[str]


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CustomerProfileOut = pydantic_model_creator(
    Customer, name="CustomerProfileOut", exclude=['account'], config_class=Config
)

CustomerProfileIn = pydantic_model_creator(
    Customer,
    name="CustomerProfileIn",
    exclude=["id", "created_at", "modified_at"],
    exclude_readonly=True,
    config_class=Config,
)
