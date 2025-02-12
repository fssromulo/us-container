# Python imports

# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_credit_card import OrderCreditCard


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderCreditCardInSchema = pydantic_model_creator(
    OrderCreditCard, name="OrderCreditCardIn", exclude_readonly=True, config_class=Config
)

OrderCreditCardOutSchema = pydantic_model_creator(
    OrderCreditCard,
    name="OrderCreditCardOut",
    include=(
        "id",
        "order_id" "merchant_name",
        "card_type",
        "response_from_gateway",
    ),
)
