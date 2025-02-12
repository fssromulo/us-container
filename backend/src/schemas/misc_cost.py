# pip imports 
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

#internal imports
from src.database.models.misc_cost import MiscCost

class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

MiscCostIn = pydantic_model_creator(
    MiscCost,
    name="MiscCostIn",
    exclude=("id","created_at","modified_at"),
    exclude_readonly=True,
    config_class=Config
)

MiscCostOut = pydantic_model_creator(
    MiscCost,
    name="MiscCostOut",
    # config_class=Config
    exclude=("order.customer, order.account, order.user"),
    exclude_readonly=True
)

class UpdateMiscCost(BaseModel):
    id: Optional[str]
    amount: Optional[Decimal]
    cost_type_id: Optional[str]