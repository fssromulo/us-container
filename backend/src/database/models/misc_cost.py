# Pip imports
from tortoise import fields, models


class MiscCost(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    cost_type = fields.ForeignKeyField("models.CostType", related_name="misc_cost", index=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    order = fields.ForeignKeyField("models.Order", related_name="misc_cost", index=True)

    class Meta:
        table = "misc_cost"

    def __str__(self):
        return f"{self.cost_type}: {self.amount}"
