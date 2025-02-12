# Python imports
import uuid

# Pip imports
from tortoise import fields, models

# Internal imports
from src.database.models.inventory.purchase_types import PurchaseTypes


class Inventory(models.Model):
    id = fields.CharField(pk=True, max_length=255, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    total_cost = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = fields.TextField(null=True)
    purchase_type = fields.CharEnumField(PurchaseTypes, max_length=50, null=True)
    invoice_number = fields.TextField(null=True)
    invoiced_at = fields.DatetimeField(null=True)
    pickup_at = fields.DatetimeField(null=True)
    payment_type = fields.TextField(null=True)
    paid_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
