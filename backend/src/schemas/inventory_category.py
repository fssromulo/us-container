# Python imports
from datetime import datetime
from decimal import Decimal
from typing import Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.inventory.inventory_category import InventoryCategory


InventoryCategoryIn = pydantic_model_creator(InventoryCategory, name="InventoryCategoryIn", exclude_readonly=True)

InventoryCategoryOut = pydantic_model_creator(InventoryCategory, name="InventoryCategoryOut")
