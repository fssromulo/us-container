# Pip imports
from tortoise import fields, models


class Reports(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField()
    query = fields.TextField()
    run_by = fields.TextField()
    run_at = fields.DatetimeField()
    result = fields.JSONField(null=True)
    query_hash = fields.TextField()
    status = fields.TextField()
    account = fields.ForeignKeyField("models.Account", related_name="reports", index=True)

    class PydanticMeta:
        exclude = ["created_at", "updated_at", "account"]

    class Meta:
        table = "reports"

    def __str__(self):
        return f"{self.id}"
