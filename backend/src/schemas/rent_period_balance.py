# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_balance import RentPeriodBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodBalanceIn = pydantic_model_creator(
    RentPeriodBalance,
    name="RentPeriodBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodBalanceOut = pydantic_model_creator(RentPeriodBalance, name="RentPeriodBalanceOut")
