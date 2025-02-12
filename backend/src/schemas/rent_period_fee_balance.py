# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_fee_balance import RentPeriodFeeBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodFeeBalanceIn = pydantic_model_creator(
    RentPeriodFeeBalance,
    name="RentPeriodFeeBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodFeeBalanceOut = pydantic_model_creator(
    RentPeriodFeeBalance, name="RentPeriodFeeBalanceOut"
)
