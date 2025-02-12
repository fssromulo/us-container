# Pip imports
from tortoise import fields, models


class CustomerApplicationSchema(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    full_schema_name = fields.CharField(50, null=True)
    name = fields.CharField(30, null=True)
    content = fields.JSONField()
    account = fields.ForeignKeyField("models.Account", related_name="application_schema", index=True)

    class Meta:
        table = "customer_application_schema"

    class PydanticMeta:
        exclude = ["account", "order"]
