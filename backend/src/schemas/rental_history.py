# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.rental_history import RentalHistory


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


RentalHistoryIn = pydantic_model_creator(
    RentalHistory,
    name="RentalHistoryIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,)

RentalHistoryUpdate = pydantic_model_creator(
    RentalHistory,
    name="RentalHistoryUpdate",
    exclude=("id", "created_at", "modified_at", "line_item_id", "inventory_id"),
    exclude_readonly=True,
    config_class=Config,)

RentalHistoryOut = pydantic_model_creator(
    RentalHistory,
    name="RentalHistoryOut",
    exclude=("account", "line_items", "line_item"),
)
