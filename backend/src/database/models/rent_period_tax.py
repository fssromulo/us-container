# Pip imports
from tortoise import fields, models


class RentPeriodTax(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    tax_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    rent_period = fields.ForeignKeyField("models.RentPeriod", related_name="rent_period_taxes", index=True)

    class Meta:
        table = "rent_period_tax"

    def __str__(self):
        return f"{self.tax_amount}"
