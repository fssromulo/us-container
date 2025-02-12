# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.inventory import Inventory
from src.database.models.inventory.inventory_status import InventoryStatus
from src.database.models.inventory.other_inventory import OtherInventory
from src.database.models.inventory.purchase_types import PurchaseTypes


class CreateUpdateInventory(BaseModel):
    total_cost: Optional[Decimal]
    condition: Optional[str]
    container_number: Optional[str]
    container_release_number: Optional[str]
    status: Optional[InventoryStatus]
    type: Optional[dict]
    container_size: Optional[str]
    purchase_type: Optional[PurchaseTypes]
    vendor_id: Optional[str]
    depot_id: Optional[str]
    invoice_number: Optional[str]
    invoiced_at: Optional[datetime]
    pickup_at: Optional[datetime]
    payment_type: Optional[str]
    paid_at: Optional[datetime]
    quantity: Optional[int]
    product_id: Optional[str]
    purchased_at: Optional[datetime]
    surcharge_fee: Optional[datetime]
    container_color: Optional[str]
    image_urls: Optional[List[Dict]]
    description: Optional[str]
    revenue: Optional[float]


InventoryIn = pydantic_model_creator(Inventory, name="InventoryIn", exclude_readonly=True)

InventoryOut = pydantic_model_creator(Inventory, name="InventoryOut")
CreateOtherInventoryIn = pydantic_model_creator(OtherInventory, exclude_readonly=True, name="CreateOtherInventoryIn")


class CreateOtherInventory(BaseModel):
    delivered: Optional[str]
    invoice_number: Optional[str]
    product_id: Optional[str]
    quantity: Optional[str]
    tracking_number: Optional[str]
    vendor_id: Optional[str]
    line_item_id: Optional[str]
    cost: Optional[Decimal]
    price: Optional[Decimal]
