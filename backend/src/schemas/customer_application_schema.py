# Python imports
from typing import Optional
from typing import List, Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.customer_application_schema import CustomerApplicationSchema

CustomerApplicationSchemaSchemaIn = pydantic_model_creator(CustomerApplicationSchema, name="CustomerApplicationSchemaSchemaIn", exclude_readonly=True)

CustomerApplicationSchemaSchemaOut = pydantic_model_creator(
    CustomerApplicationSchema,
    name="CustomerApplicationSchemaSchemaOut"
)