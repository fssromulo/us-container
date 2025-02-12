# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_total_balance import RentPeriodTotalBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodTotalBalanceIn = pydantic_model_creator(
    RentPeriodTotalBalance,
    name="RentPeriodTotalBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodTotalBalanceOut = pydantic_model_creator(
    RentPeriodTotalBalance, name="RentPeriodTotalBalanceOut", exclude_readonly=True
)
