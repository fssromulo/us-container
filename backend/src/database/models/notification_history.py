# Pip imports
from tortoise import fields, models


class NotificationHistory(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    order_id = fields.UUIDField(null=True)
    line_item_id = fields.UUIDField(null=True)
    user_id = fields.UUIDField(null=True)
    notification = fields.ForeignKeyField("models.Notification", related_name="notification_history", index=True)
    notification_content = fields.TextField(null=True)
    sent_by_provider = fields.TextField(null=True)
    response_from_provider = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="notification_history", index=True)
    
    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = "notification_history"
