# Pip imports
from tortoise import fields, models


class Commission(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    user = fields.ForeignKeyField("models.User", related_name="commission")
    flat_commission = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    commission_percentage = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    commission_effective_date = fields.DatetimeField()
    rental_total_flat_commission_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    rental_effective_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    accessory_commission_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    class PydanticMeta:
        exclude = ["account"]

    class Meta:
        table = "commission_rates"
