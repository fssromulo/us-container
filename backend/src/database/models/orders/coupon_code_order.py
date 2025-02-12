# Pip imports
from tortoise import fields, models


class CouponCodeOrder(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    order = fields.ForeignKeyField("models.Order", related_name="coupon_code_order")
    coupon = fields.ForeignKeyField("models.CouponCode", related_name="coupon_code_order")

    class PydanticMeta:
        exclude = [
            "created_at",
            "modified_at",
        ]

    class Meta:
        table = "coupon_code_order"
        db = "default"  # Set the default connection here

    def __str__(self):
        return f"{self.id}"
