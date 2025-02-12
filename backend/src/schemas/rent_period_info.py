# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel


class UpdateRentPeriodInfo(BaseModel):
    rent_period_id: Optional[str]
    balance_amt: Optional[Decimal]
    tax_amt: Optional[Decimal]
    amount_owed: Optional[Decimal]


class UpdatePeriodPrice(BaseModel):
    order_id: Optional[str]
    price: Optional[Decimal]

class AddRentalPeriods(BaseModel):
    order_id: Optional[str]
    number_of_period: Optional[int]

class UpdatedPeriod(BaseModel):
    date: Optional[str]
    id: Optional[str]
    rent_due_on_day: Optional[int]
    order_id: Optional[str]
class UpdatePeriodDueDate(BaseModel):
    updated_period: Optional[UpdatedPeriod]
    subsequent_period_ids: list[str] = []
