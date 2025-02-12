# Pip imports
from tortoise import fields, models


class OrderFeeBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    account = fields.ForeignKeyField("models.Account", related_name="account_order_fee_balance", index=True)
    order = fields.ForeignKeyField("models.Order", related_name="order_fee_balance", index=True)
    remaining_balance = fields.DecimalField(max_digits=10, decimal_places=2)
    fee = fields.ForeignKeyField("models.Fee", related_name="fee_balance", index=True)
    transaction_type = fields.ForeignKeyField("models.TransactionType", related_name="order_fee_balance", null=True)
    order_credit_card = fields.ForeignKeyField("models.OrderCreditCard", related_name="order_fee_balance", null=True)

    class PydanticMeta:
        exclude = [
            "modified_at",
            "account",
            "order",
            "transaction_type",
            "order_credit_card"
        ]

    class Meta:
        table = "order_fee_balance"

    def __str__(self):
        return f"{self.id}"
