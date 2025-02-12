# Python imports
from datetime import datetime
from typing import Optional

# Pip imports
from tortoise import fields, models


class CouponCode(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    minimum_discount_threshold = fields.DecimalField(max_digits=10, decimal_places=2)
    name = fields.TextField()
    code = fields.CharField(unique=True, max_length=20)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    city = fields.JSONField(null=True)
    size = fields.JSONField(null=True)
    is_permanent = fields.BooleanField(null=True)
    type = fields.TextField(null=True)
    role = fields.JSONField(null=True)
    rules = fields.JSONField(null=True)
    is_stackable = fields.BooleanField(null=False)
    account = fields.ForeignKeyField("models.Account", related_name="coupons")
    category = fields.TextField(null=True)
    percentage = fields.IntField(null=True)
    attributes = fields.JSONField(null=True)

    def is_expired(self) -> Optional[bool]:
        current_datetime = datetime.now().replace(tzinfo=None)
        return current_datetime >= self.end_date.replace(tzinfo=None) if self.end_date.replace(tzinfo=None) else False

    class PydanticMeta:
        exclude = ["created_at", "modified_at", "account"]
        computed = ("is_expired",)

    class Meta:
        table = "coupon_code"

    def __str__(self):
        return f"{self.id}"
