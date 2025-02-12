# Pip imports
from tortoise import fields, models


class CMS(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    attributes = fields.JSONField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="cms")

    class PydanticMeta:
        exclude = ["account"]

    class Meta:
        table = "cms"
