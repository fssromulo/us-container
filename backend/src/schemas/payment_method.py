# Python imports
from typing import Optional
from typing import List, Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.payment_method import PaymentMethod


PaymentMethodInSchema = pydantic_model_creator(PaymentMethod, name="PaymentMethodIn", exclude_readonly=True)

PaymentMethodOutSchema = pydantic_model_creator(
    PaymentMethod,
    name="PaymentMethodOut",
)


class CreateUpdatePaymentMethodZone(BaseModel):
    name: Optional[str]
    display_name: Optional[str]