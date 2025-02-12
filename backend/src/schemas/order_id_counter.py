# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_id_counter import OrderIdCounter


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderIdCounterIn = pydantic_model_creator(
    OrderIdCounter, name="OrderIdCounterIn", include=("account_id", "order_id"), config_class=Config
)

OrderIdCounterUpdate = pydantic_model_creator(
    OrderIdCounter, name="OrderIdCounterUpdate", exclude_readonly=True, exclude=("account",), config_class=Config
)

OrderIdCounterOut = pydantic_model_creator(OrderIdCounter, name="OrderIdCounterOut", exclude=("account",))
