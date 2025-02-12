# Pip imports
from tortoise import fields, models


class RentPeriodTotalBalance(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    remaining_balance = fields.DecimalField(max_digits=10, decimal_places=2)
    rent_period = fields.ForeignKeyField("models.RentPeriod", related_name="rent_period_total_balances", index=True)

    class Meta:
        table = "rent_period_total_balance"

    def __str__(self):
        return f"{self.rent_period}: Total Remaining Balance: {self.remaining_balance}"
