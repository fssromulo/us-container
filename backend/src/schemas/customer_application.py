# Python imports

# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra, Json
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.customer_application_response import CustomerApplicationResponse
from src.database.models.customer_application_schema import CustomerApplicationSchema


class UpdateCustomerApplicationSchema(BaseModel):
    content: Optional[str]


class CreateUpdateCustomerApplicationResponse(BaseModel):
    response_content: Optional[Json]
    accepted: Optional[bool]
    order_id: Optional[str]
    schema_id: Optional[str]
    contract_detail: Optional[str]


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CustomerApplicationResponseOut = pydantic_model_creator(
    CustomerApplicationResponse, name="CustomerApplicationResponseOut", exclude=["account"], config_class=Config
)

CustomerApplicationResponseIn = pydantic_model_creator(
    CustomerApplicationResponse,
    name="CustomerApplicationResponseIn",
    exclude=["id", "created_at", "modified_at"],
    exclude_readonly=True,
    config_class=Config,
)

CustomerApplicationResponseOut = pydantic_model_creator(
    CustomerApplicationResponse, name="CustomerApplicationResponseOut", config_class=Config
)

CustomerApplicationSchemaIn = pydantic_model_creator(
    CustomerApplicationSchema,
    name="CustomerApplicationSchemaIn",
    exclude=["created_at", "modified_at"],
)

CustomerApplicationSchemaOut = pydantic_model_creator(
    CustomerApplicationSchema,
    name="CustomerApplicationSchemaOut",
    exclude=["account"],
)
