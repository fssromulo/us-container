# Python imports
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

# Pip imports
from tortoise import fields, models
from tortoise.exceptions import NoValuesFetched


class Product(models.Model):
    id = fields.UUIDField(pk=True, max_length=255, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField(null=True)
    description = fields.TextField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    monthly_price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost_per_mile = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    minimum_shipping_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    location = fields.ForeignKeyField("models.LocationPrice", null=True, index=True)
    product_category = fields.ForeignKeyField("models.ProductCategory", null=True, index=True)

    class Meta:
        abstract = True

    class PydanticMeta:
        exclude = ["account"]
