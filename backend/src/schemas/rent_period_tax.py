# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period_tax import RentPeriodTax


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodTaxIn = pydantic_model_creator(
    RentPeriodTax,
    name="RentPeriodTaxIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodTaxOut = pydantic_model_creator(RentPeriodTax, name="RentPeriodTaxOut", exclude_readonly=True)
