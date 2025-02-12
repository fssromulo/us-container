# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Type

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.orders.line_item import LineItem
from src.schemas.notes import UpdateNote


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


class UpdateLineItem(BaseModel):
    id: Optional[str]
    potential_dollar_per_mile: Optional[Decimal]
    potential_miles: Optional[Decimal]
    product_cost: Optional[Decimal]
    welcome_call: Optional[str]
    good_to_go: Optional[str]
    revenue: Optional[Decimal]
    shipping_revenue: Optional[Decimal]
    scheduled_date: Optional[datetime]
    shipping_cost: Optional[Decimal]
    # tax: Optional[Decimal]
    door_orientation: Optional[str]
    missed_delivery: Optional[bool]
    product_city: Optional[str]
    product_state: Optional[str]
    container_size: Optional[str]
    condition: Optional[str]
    attributes: Optional[Dict]
    notes: Optional[UpdateNote]
    inventory_id: Optional[str]
    driver_id: Optional[str]
    returned_at: Optional[datetime]
    potential_date: Optional[datetime]
    delivery_date: Optional[datetime]

    class Config:
        extra = 'allow'

    def get_all_field_names(self, line_item) -> List[str]:
        return get_field_names(line_item)


class UpdateLineItemExtra(BaseModel):
    lineItems: List[UpdateLineItem]
    inventoryIdsToMakeAvailable: List[str]
    move_out_date: Optional[datetime]
    move_out_type: Optional[str]
    is_move_out: Optional[bool]



def get_field_names(model: Type[BaseModel]) -> List[str]:
    return [field_name for field_name, field_value in model.__dict__.items() if field_value is not None]


class CreateLineItem(BaseModel):
    potential_dollar_per_mile: Optional[Decimal]
    potential_miles: Optional[Decimal]
    product_cost: Optional[Decimal]
    product_id: Optional[str]
    product_type: Optional[str]
    good_to_go: Optional[str]
    scheduled_date: Optional[str]
    welcome_call: Optional[str]
    missed_delivery: Optional[bool]
    revenue: Optional[Decimal]
    shipping_revenue: Optional[Decimal]
    shipping_cost: Optional[Decimal]
    tax: Optional[Decimal]
    door_orientation: Optional[str]
    product_city: Optional[str]
    product_state: Optional[str]
    container_size: Optional[str]
    monthly_owed: Optional[Decimal]
    interest_owed: Optional[Decimal]
    total_rental_price: Optional[Decimal]
    rent_period: Optional[Decimal]
    condition: Optional[str]
    attributes: Optional[Dict]
    note: Optional[UpdateNote]
    inventory_id: Optional[str]
    convenience_fee: Optional[Decimal]
    other_product_id: Optional[str]
    product_type: Optional[str]
    file_upload_id: Optional[str]


line_item_update_includes = [
    'scheduled_date',
    'potential_date',
    'minimum_shipping_cost',
    'potential_dollar_per_mile',
    'potential_miles',
    'product_cost',
    'revenue',
    'shipping_revenue',
    'shipping_cost',
    'tax',
    'potential_driver_charge',
    'convenience_fee',
    'good_to_go',
    'welcome_call',
    'pickup_email_sent',
    'missed_delivery',
    'door_orientation',
    'product_city',
    'product_state',
    'container_size',
    'condition',
    'inventory_id',
    'driver_id',
    'potential_driver_id',
    "attributes",
    "rent_period",
    "interest_owed",
    "total_rental_price",
    "monthly_owed",
]

line_item_includes_usac = line_item_update_includes.copy()
line_item_includes_usac.append('id')
line_item_includes_usac.append('order_id')

LineItemIn = pydantic_model_creator(
    LineItem, name="LineItemIn", exclude=("id", "created_at", "modified_at"), exclude_readonly=True
)

LineItemInUpdate = pydantic_model_creator(LineItem, name="LineItemInUpdate", exclude_readonly=True)

LineItemOut = pydantic_model_creator(
    LineItem, name="LineItemOut", exclude=("inventory.vendor.note", "inventory.depot.note")
)
