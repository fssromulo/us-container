# Pip imports
from tortoise import fields, models


class RentPeriodFeeBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    remaining_balance = fields.DecimalField(max_digits=10, decimal_places=2)
    rent_period = fields.ForeignKeyField("models.RentPeriod", related_name="rent_period_fee_balances", index=True)
    transaction_type = fields.ForeignKeyField(
        "models.TransactionType", related_name="rent_period_fee_balance", null=True
    )
    order_credit_card = fields.ForeignKeyField(
        "models.OrderCreditCard", related_name="rent_period_fee_balance", null=True
    )

    class Meta:
        table = "rent_period_fee_balance"

    def __str__(self):
        return f"{self.rent_period}: {self.remaining_balance}"
