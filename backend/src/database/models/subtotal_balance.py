# Pip imports
from tortoise import fields, models


class SubtotalBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    order = fields.ForeignKeyField("models.Order", related_name="subtotal_balance", index=True)
    balance = fields.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = fields.ForeignKeyField("models.TransactionType", related_name="subtotal_balance", null=True)
    order_credit_card = fields.ForeignKeyField("models.OrderCreditCard", related_name="subtotal_balance", null=True)

    class PydanticMeta:
        exclude = [
            "modified_at",
            "account",
            "order",
            "order_credit_card",
            "transaction_type"
        ]

    class Meta:
        table = "subtotal_balance"

    def __str__(self):
        return f"{self.id}"
