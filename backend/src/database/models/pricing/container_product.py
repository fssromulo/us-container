# Python imports
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

# Pip imports
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched

# Internal imports
from src.database.models.pricing.product import Product


class ContainerProduct(Product):
    container_size = fields.TextField(null=True)
    height = fields.IntField(null=True)
    width = fields.IntField(null=True)
    length = fields.IntField(null=True)
    condition = fields.TextField(null=True)
    product_type = fields.TextField(null=True)
    pod = fields.BooleanField(null=True)

    class Meta:
        table = "container_product"

    class PydanticMeta:
        exclude = ["location.account", "container_inventory"]
        computed = ("title",)

    def title(self) -> str:
        try:
            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "High Cube":
                    found = True

            high_cube = "High Cube" if found else "Standard"
            
            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "High Cube":
                    found = True

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "Double Door":
                    found = True

            double_door = "Double Door" if found else ""

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "Premium":
                    found = True

            premium = "Premium" if found else ""

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "WWT/CW":
                    found = True

            wwt = "WWT/CW" if found else ""

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "AS IS":
                    found = True

            as_is = "AS IS" if found else ""

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "Open Side":
                    found = True

            open_side = "Open Side" if found else ""

            found = False
            for cpa in self.container_product_attributes:
                if hasattr(cpa.container_attribute, "name") and cpa.container_attribute.name == "Side Doors":
                    found = True

            side_doors = "Side Doors" if found else ""


            type = f"{high_cube} {open_side} {side_doors} {double_door} {as_is} {premium} {wwt}".strip()
            type = " ".join(filter(lambda x: True if x != '' else False, type.split(" ")))
            product_type = None
            product_type = "" if self.product_type == "SHIPPING_CONTAINER" else "Portable"
            return f"{self.container_size}' {self.condition} {type} {product_type}".strip()
        except NoValuesFetched:
            return ""
