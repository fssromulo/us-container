# Pip imports
from tortoise import fields, models


class Role(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    role_id = fields.TextField()
    name = fields.TextField(null=True)
    sales_commission_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    rental_commission_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    accessory_default_commission_rate = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    account = fields.ForeignKeyField("models.Account", related_name="role_account")

    class PydanticMeta:
        exclude = ["account"]

    class Meta:
        table = "role"
