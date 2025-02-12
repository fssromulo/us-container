# Pip imports
from tortoise import fields, models


class VendorType(models.Model):
    id = fields.IntField(pk=True)
    type = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    account = fields.ForeignKeyField("models.Account", related_name="vendor_types", index=True)

    class Meta:
        table = "vendor_type"

    class PydanticMeta:
        exclude = ["account"]
