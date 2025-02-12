# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_comission import OrderCommision


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderCommissionIn = pydantic_model_creator(
    OrderCommision, name="OrderCommissionIn", exclude_readonly=True, config_class=Config
)

OrderCommissionOut = pydantic_model_creator(
    OrderCommision,
    name="OrderCommissionOut",
)
