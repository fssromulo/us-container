# Pip imports
from tortoise import fields, models


class CouponLineItemValue(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    line_item = fields.ForeignKeyField("models.LineItem", related_name="coupon_line_item_values", null=True)
    coupon_code_order = fields.ForeignKeyField("models.CouponCodeOrder", related_name="coupon_line_item_value", null=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2) #Amount applied to line_item
    class PydanticMeta:
        exclude = [
            "created_at",
            "modified_at",
        ]

    class Meta:
        table = "coupon_line_item_value"
        db = "default"  # Set the default connection here

    def __str__(self):
        return f"{self.id}"
