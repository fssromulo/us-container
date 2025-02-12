# Pip imports
from tortoise import fields, models


class TaxBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    order = fields.ForeignKeyField("models.Order", related_name="tax_balance", index=True)
    balance = fields.DecimalField(max_digits=10, decimal_places=4)
    tax_rate = fields.DecimalField(max_digits=10, decimal_places=4)
    transaction_type = fields.ForeignKeyField("models.TransactionType", related_name="tax_balance", null=True)
    order_credit_card = fields.ForeignKeyField("models.OrderCreditCard", related_name="tax_balance", null=True)

    class PydanticMeta:
        exclude = [
            "modified_at",
            "account",
        ]

    class Meta:
        table = "tax_balance"

    def __str__(self):
        return f"{self.id}"
