# Pip imports
from tortoise import fields, models


class OrderTax(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    tax_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    order = fields.ForeignKeyField("models.Order", related_name="order_tax", index=True)
    class Meta:
        table = "order_tax"

    def __str__(self):
        return f"{self.tax_amount}"
