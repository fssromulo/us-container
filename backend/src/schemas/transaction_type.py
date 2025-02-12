# Python imports
from datetime import datetime
from typing import List, Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.transaction_type import TransactionType


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


TransactionTypeIn = pydantic_model_creator(
    TransactionType,
    name="TransactionTypeIn",
    exclude=("created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
    optional=("account_id", "id"),
)

TransactionTypeInUpdate = pydantic_model_creator(
    TransactionType,
    name="TransactionTypeInUpdate",
    optional=[
        "account_id",
        "id",
        "order",
        "rent_period",
        "account",
        "credit_card_object",
        "user",
        "transaction_effective_date",
        "amount",
        "notes",
        "payment_type",
    ],
    exclude_readonly=True,
    config_class=Config,
)

TransactionTypeOut = pydantic_model_creator(TransactionType, name="TransactionTypeOut", exclude=("order", "account"))


class TransactionTypeInDto(BaseModel):
    """DTO for incoming transaction type data."""

    id: Optional[str]
    payment_type: Optional[str]
    notes: Optional[str]
    amount: Optional[float]
    transaction_effective_date: Optional[datetime]


class TransactionTypesIn(BaseModel):
    rent_period_ids: list = []
    order_id: Optional[str]
    notes: Optional[str]
    payment_type: Optional[str]
    amount: Optional[List[float]]
    account_id: Optional[int]
