# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_tax_balance import RentPeriodTaxBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodTaxBalanceIn = pydantic_model_creator(
    RentPeriodTaxBalance,
    name="RentPeriodTaxBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)


RentPeriodTaxBalanceOut = pydantic_model_creator(
    RentPeriodTaxBalance,
    name="RentPeriodTaxBalanceOut"
)
