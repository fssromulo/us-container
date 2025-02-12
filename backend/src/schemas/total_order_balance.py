# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.total_order_balance import TotalOrderBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


TotalOrderBalanceIn = pydantic_model_creator(
    TotalOrderBalance,
    name="TotalOrderBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

TotalOrderBalanceOut = pydantic_model_creator(
    TotalOrderBalance,
    name="TotalOrderBalanceOut",
    exclude_readonly=True,
)
