# Pip imports
from tortoise import fields, models


class Audit(models.Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(null=True)
    updated_at = fields.DatetimeField(auto_now_add=True)
    entity_name = fields.TextField()
    object_id = fields.CharField(50, null=True)
    request_data = fields.JSONField(null=True)
    operation_type = fields.TextField()
    request_url = fields.TextField()
    group_id = fields.UUIDField()

    class Meta:
        table = "audit"

    def __str__(self):
        return f"{self.id}"
