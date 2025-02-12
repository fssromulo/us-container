# Pip imports
from tortoise import fields, models


class PaymentMethod(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField(null=True)
    display_name = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="payment_methods_account")

    class Meta:
        table = "payment_method"

    class PydanticMeta:
        exclude = ["account"]

    def __str__(self):
        return f"{self.id}"
