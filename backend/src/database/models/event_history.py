# Pip imports
from tortoise import fields, models


class EventHistory(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    action = fields.TextField()
    account = fields.ForeignKeyField("models.Account", related_name="history")

    class Meta:
        table = "event_history"

    def __str__(self):
        return f"{self.action}"
