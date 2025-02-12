# Python imports
from typing import List, Optional

# Pip imports
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.vendor_types import VendorType


VendorTypeInSchema = pydantic_model_creator(VendorType, name="VendorTypeIn", exclude_readonly=True)

VendorTypeOutSchema = pydantic_model_creator(VendorType, name="VendorTypeOut")
