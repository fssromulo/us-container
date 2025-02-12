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
from src.database.models.inventory.inventory import Inventory


class OtherInventory(Inventory):
    id = fields.CharField(pk=True, max_length=255)
    product = fields.ForeignKeyField("models.OtherProduct", related_name="other_inventory", null=True)
    tracking_number = fields.TextField(null=True)
    quantity = fields.IntField(null=True)
    delivered = fields.TextField(null=True)
    vendor = fields.ForeignKeyField("models.Vendor", related_name="other_inventory", null=True)
    account = fields.ForeignKeyField("models.Account", related_name="other_inventory", index=True)

    class Meta:
        table = "other_inventory"

    class PydanticMeta:
        exclude = [
            "account",
        ]
