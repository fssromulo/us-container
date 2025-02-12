# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.subtotal_balance import SubtotalBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


SubtotalBalanceIn = pydantic_model_creator(
    SubtotalBalance,
    name="SubtotalBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

SubtotalBalanceIn2 = pydantic_model_creator(
    SubtotalBalance,
    name="SubtotalBalanceIn",
    exclude=("id", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

SubtotalBalanceOut = pydantic_model_creator(
    SubtotalBalance,
    name="SubtotalBalanceOut",
    include=('id', 'created_at', 'order_id', 'balance', 'transaction_type_id', 'order_credit_card_id'),
)
