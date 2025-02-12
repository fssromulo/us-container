# Python imports
from typing import List, Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.reports import Reports


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


ReportsOut = pydantic_model_creator(
    Reports, name="ReportsOut", exclude=['updated_at', 'created_at'], config_class=Config
)

ReportsInUpdate = pydantic_model_creator(
    Reports, name="ReportsInUpdate", exclude=("name", "query", "run_by", "run_at", "query_hash"), exclude_readonly=True
)


ReportsIn = pydantic_model_creator(
    Reports,
    name="ReportsIn",
    exclude=["id", "created_at", "updated_at"],
    exclude_readonly=True,
    config_class=Config,
)


class FilterObject(BaseModel):
    begin_date: Optional[str]
    end_date: Optional[str]
    conditions: Optional[List[str]]
    productTypes: Optional[List[str]]
    statuses: Optional[List[str]]
    states: Optional[List[str]]
    account_id: Optional[int]
    role_id: Optional[str]
    run_by: Optional[str]
    purchase_type: Optional[str]
    vendors: Optional[List[str]]
    order_ids: Optional[List[str]]
    manager: Optional[bool]
    can_read_all: Optional[bool]
    user_id: Optional[str]
    purchase_types: Optional[List[str]]