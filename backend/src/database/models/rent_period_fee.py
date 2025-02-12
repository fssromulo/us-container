# Pip imports
from tortoise import fields, models

# Internal imports
from src.database.models.orders.fee_type import FeeType


class RentPeriodFee(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    fee_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    fee_type = fields.CharEnumField(FeeType, max_length=50, null=True)
    due_at = fields.DatetimeField(null=True)
    description = fields.TextField(null=True)
    rent_period = fields.ForeignKeyField("models.RentPeriod", related_name="rent_period_fees", index=True)
    type = fields.ForeignKeyField(
        "models.FeeType", related_name="rent_period_fees", index=True, null=True
    )  # TODO SET THIS BACK TO NOT NULL ONCE MIGRATION IS COMPETE

    class Meta:
        table = "rent_period_fee"

    def __str__(self):
        return f"{self.fee_type}: {self.fee_amount}, {self.due_at}"
