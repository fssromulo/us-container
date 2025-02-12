# Python imports

# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.customer.order_customer import OrderCustomer
from src.database.models.orders.payment_options import PaymentOptions

from .notes import UpdateNote
from .orders import CreateOrder, UpdateOrder


class UpdateCustomerOrder(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    street_address: Optional[str]
    phone: Optional[str]
    zip: Optional[str]
    state: Optional[str]
    city: Optional[str]
    email: Optional[str]
    company_name: Optional[str]
    county: Optional[str]
    note: Optional[UpdateNote]
    order: Optional[UpdateOrder]


class CreateCustomerOrder(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    street_address: Optional[str]
    phone: Optional[str]
    zip: Optional[str]
    state: Optional[str]
    city: Optional[str]
    email: Optional[str]
    county: Optional[str]
    note: Optional[UpdateNote]
    order: Optional[CreateOrder]
    payment_type: Optional[PaymentOptions]
    company_name: Optional[str]

exclusions = [
    "account",
    "order.account",
    "order.account_id",
    "order.user.sales_assistant",
    "order.user.manager",
    "order.user.team_member",
    "order.user.team_lead",
    "order.user.note",
    "order.user.account",
    "street_address",
    "zip",
    "state",
    "city",
    "county",
]


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CustomerOut = pydantic_model_creator(OrderCustomer, name="CustomerOut", exclude=exclusions, config_class=Config)
CustomerDetailOut = pydantic_model_creator(OrderCustomer, name="CustomerDetailOut", exclude=["account", "created_at", "modified_at", "note"], config_class=Config)

CustomerIn = pydantic_model_creator(
    OrderCustomer,
    name="CustomerIn",
    exclude=["id", "created_at", "modified_at"],
    exclude_readonly=True,
    config_class=Config,
)

CustomerInUSAC = pydantic_model_creator(
    OrderCustomer,
    name="CustomerInUSAC",
    exclude=["created_at", "modified_at", "note", "order", "account"],
)

class CustomerDetail(BaseModel):
    name: Optional[str]
    email: Optional[str]
    address: Optional[str]
    delivery_address: Optional[str]
