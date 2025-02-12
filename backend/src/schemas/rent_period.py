# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rent_period import RentPeriod


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentPeriodIn = pydantic_model_creator(
    RentPeriod,
    name="RentPeriodIn",
    exclude=("id", "created_at", "modified_at"),
    optional=("order_id", "end_date", "start_date"),
    exclude_readonly=True,
    config_class=Config,
)

RentPeriodOut = pydantic_model_creator(RentPeriod, name="RentPeriodOut", exclude=("order"))  #
# TODO fix this up so that it has some level of exlusion so that it doesnt returne everything... potentially
# if it doesnt have any joins then it could be ok, or if those joins are needed...

RentPeriodOutOrderOut = pydantic_model_creator(
    RentPeriod, name="RentPeriodOutOrderOut", exclude=['order']
)  # , exclude=("order")
