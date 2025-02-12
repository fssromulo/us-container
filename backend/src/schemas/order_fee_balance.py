# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_fee_balance import OrderFeeBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderFeeBalanceIn = pydantic_model_creator(
    OrderFeeBalance,
    name="OrderFeeBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

OrderFeeBalanceIn2 = pydantic_model_creator(
    OrderFeeBalance,
    name="OrderFeeBalanceIn",
    exclude=("id", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

OrderFeeBalanceOut = pydantic_model_creator(
    OrderFeeBalance,
    name="OrderFeeBalanceOut",
    include=(
        'id',
        'created_at',
        'order_id',
        'remaining_balance',
        'transaction_type_id',
        'order_credit_card_id',
        "fee_id",
    ),
)
