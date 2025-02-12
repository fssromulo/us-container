
# Pip imports
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseConfig, BaseModel, Extra
from typing import Dict, List, Optional, Type

# Internal imports
from src.database.models.fee_type import FeeType


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

FeeTypeIn = pydantic_model_creator(
    FeeType,
    name="FeeTypeIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

FeeTypeOut = pydantic_model_creator(
    FeeType,
    name="FeeTypeOut",
    exclude_readonly=True
)

class FeeTypeUpdate(BaseModel):
    is_archived: Optional[bool]
    is_taxable: Optional[bool]
    adjusts_profit: Optional[bool]
    name: Optional[str]
    display_name: Optional[str]
