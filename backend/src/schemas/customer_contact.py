# Python imports

# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.customer.customer_contact import CustomerContact


class CreateCustomerContact(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    customer_id: Optional[str]
    customer_address_id: Optional[str]


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CustomerContactOut = pydantic_model_creator(
    CustomerContact, name="CustomerContactOut", exclude=["account"], config_class=Config
)

CustomerContactIn = pydantic_model_creator(
    CustomerContact,
    name="CustomerContactIn",
    exclude=["id", "created_at", "modified_at"],
    exclude_readonly=True,
    config_class=Config,
)

class NewCustomerContact(BaseModel):
    customer_address: Optional[str]
    customer_id	: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    account_id: Optional[int]
    zip: Optional[str]
    city: Optional[str]
    street_address: Optional[str]
    state: Optional[str]
    county: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

class EditCustomerContact(BaseModel):
    customer_address: Optional[str]
    customer_id	: Optional[str]
    id	: Optional[str]
    account_id	: Optional[int]
    customer_address_id	: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    street_address: Optional[str]
    state: Optional[str]
    county: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
