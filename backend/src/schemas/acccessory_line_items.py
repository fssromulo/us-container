# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Type

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.orders.accessory_line_item import AccessoryLineItem


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True

class CreateAccessoryLineItem(BaseModel):
    id: Optional[str]
    product_type: Optional[str]
    other_product_name: Optional[str]
    other_product_shipping_time: Optional[str]
    line_item_id: Optional[str]
    filename: Optional[str]
    content_type: Optional[str]
    folder_type: Optional[str]
    other_product_id: Optional[str]
    class Config:
        extra = 'allow'

AccessoryLineItemIn = pydantic_model_creator(
    cls=AccessoryLineItem,
    name="AccessoryLineItemIn",
    exclude=(
        "id",
        "created_at",
        "modified_at",
    ),
)


AccessoryLineItemOut = pydantic_model_creator(AccessoryLineItem, name="AccessoryLineItemOut", include=(
    "id",
    "product_type",
    "other_product_name",
    "other_product_shipping_time",
    "line_item_id",
    "filename",
    "content_type",
    "folder_type",
    "other_product.product_link",
    "calculated_product_url",
))
