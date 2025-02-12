# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.comission import Commission


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CommissionIn = pydantic_model_creator(
    Commission,
    name="CommissionIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

CommissionOut = pydantic_model_creator(
    Commission,
    name="CommissionOut",
)

CommissionInUpdate = pydantic_model_creator(
    Commission, name="CommissionInUpdate", exclude=("id", "created_at", "modified_at", "user")
)


class CreateUpdateCommission(BaseModel):
    flat_commission: Optional[Decimal]
    commission_percentage: Optional[Decimal]
    commission_effective_date: Optional[datetime]
    rental_effective_rate: Optional[Decimal]
    rental_total_flat_commission_rate: Optional[Decimal]