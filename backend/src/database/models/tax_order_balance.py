# Pip imports
from tortoise import fields, models


class TaxOrderBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    remaining_balance = fields.DecimalField(max_digits=10, decimal_places=2)
    order = fields.ForeignKeyField("models.Order", related_name="tax_order_balance", index=True)

    class Meta:
        table = "tax_order_balance"

    def __str__(self):
        return f"{self.remaining_balance}"
