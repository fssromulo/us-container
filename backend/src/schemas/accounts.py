# Python imports
from typing import Optional
from typing import List, Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.account import Account


AccountInSchema = pydantic_model_creator(Account, name="AccountIn", exclude=["name"], exclude_readonly=True)

AccountOutSchema = pydantic_model_creator(
    Account,
    name="AccountOut",
    include=(
        'auth0_management_token',
        'auth0_management_token_modified_at',
        'cms_attributes',
        'integrations',
        'is_active',
        'name',
        'id',
        'created_at',
        'modified_at',
        "external_integrations"
    ),
)


class UpdateAccount(BaseModel):
    name: Optional[str]
    is_active: Optional[str]
    cms_attributes: Optional[dict]
    updated_attributes: Optional[dict]
    updating_fields: Optional[List[str]]
    type: Optional[str]
    auth0_management_token: Optional[str]
    integrations: Optional[dict]
