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
from src.database.models.pricing.region import Region


class PickupRegion(str, Enum):
    A = "PU A"
    B = "PU B"
    C = "PU C"


class LocationPrice(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    city = fields.TextField(null=True)
    state = fields.TextField(null=True)
    province = fields.TextField(null=True)
    zip = fields.TextField(null=True)
    region = fields.CharEnumField(Region, max_length=20, null=True)
    account = fields.ForeignKeyField("models.Account")
    cost_per_mile = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    minimum_shipping_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    pickup_region = fields.CharEnumField(PickupRegion, max_length=20, null=True)
    average_delivery_days = fields.IntField(default=15)

    class Meta:
        table = "location_price"

    class PydanticMeta:
        exclude = ["account", "fixed_location_prices"]
