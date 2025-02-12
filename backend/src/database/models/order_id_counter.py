# Pip imports
from tortoise import fields, models


class OrderIdCounter(models.Model):
    id = fields.UUIDField(pk=True)
    order_id = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    account = fields.ForeignKeyField("models.Account", related_name="order_id_counter")

    class Meta:
        table = "order_id_counter"
