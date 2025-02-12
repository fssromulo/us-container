# Pip imports
from tortoise import fields, models


class Notification(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField()
    subject = fields.TextField()
    type = fields.TextField()
    content = fields.TextField(null=True)
    external_id = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="notification", index=True)
    
    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = "notification"
