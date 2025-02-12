# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.fee import Fee, FeeType


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


FeeIn = pydantic_model_creator(
    Fee,
    name="FeeIn",
    exclude=(
        "id",
        "created_at",
        "modified_at",
    ),
    exclude_readonly=True,
    config_class=Config,
)


FeeOut = pydantic_model_creator(
    Fee,
    name="FeeOut",
)

FeeInUpdate = pydantic_model_creator(
    Fee,
    name="FeeInUpdate",
    exclude=("created_at", "modified_at", "order_id"),
    exclude_readonly=True,
    config_class=Config,
)


class UpdateFee(BaseModel):
    id: Optional[str]
    fee_amount: Optional[Decimal]
    fee_type: Optional[str]
    type_id: Optional[str]
    order_id: Optional[str]
    order_balance_change: Optional[Decimal]
    updated_balance_change: Optional[Decimal]
