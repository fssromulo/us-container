# Python imports
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

# Pip imports
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched


class InventoryCategory(models.Model):
    id = fields.CharField(pk=True, max_length=255)
    name = fields.TextField(null=True)

    class Meta:
        table = "inventory_category"
