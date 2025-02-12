# pip imports 
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

#internal imports
from src.database.models.cost_type import CostType

class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

CostTypeIn = pydantic_model_creator(
    CostType,
    name="CostTypeIn",
    exclude=("id","created_at","modified_at"),
    exclude_readonly=True,
    config_class=Config
)

CostTypeOut = pydantic_model_creator(
    CostType,
    name="CostTypeOut",
    exclude=("misc_cost.order", "misc_cost.user", "misc_cost.customer", "misc_cost") 
    # config_class=Config
)
