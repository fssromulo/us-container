# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.tax_balance import TaxBalance


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


TaxBalanceIn = pydantic_model_creator(
    TaxBalance,
    name="TaxBalanceIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

TaxBalanceIn2 = pydantic_model_creator(
    TaxBalance,
    name="TaxBalanceIn",
    exclude=("id", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)


TaxBalanceOut = pydantic_model_creator(
    TaxBalance,
    name="TaxBalanceOut",
    include=('id', 'created_at', 'order_id', 'balance', 'transaction_type_id', 'order_credit_card_id'),
)
