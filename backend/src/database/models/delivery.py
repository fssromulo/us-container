# Pip imports
from tortoise import fields, models


class Delivery(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    line_item = fields.ForeignKeyField("models.LineItem", related_name="deliveries")
    driver = fields.ForeignKeyField("models.Driver", related_name="deliveries")
    account = fields.ForeignKeyField("models.Account", related_name="deliveries")

    class Meta:
        table = "delivery"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
