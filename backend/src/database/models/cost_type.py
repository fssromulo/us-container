# Pip imports
from tortoise import fields, models


class CostType(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField()

    class Meta:
        table = "cost_type"

    def __str__(self):
        return f"{self.name}"
