# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_fee import RentPeriodFee


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodFeeIn = pydantic_model_creator(
    RentPeriodFee,
    name="RentPeriodFeeIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodFeeOut = pydantic_model_creator(RentPeriodFee, name="RentPeriodFeeOut", exclude_readonly=True)


class UpdateRentPeriodFee(BaseModel):
    id: Optional[str]
    fee_amount: Optional[Decimal]
    fee_type: Optional[str]
    rent_period_id: Optional[str]
    rent_period_fee_balance_change: Optional[Decimal]
    type_id: Optional[str]
