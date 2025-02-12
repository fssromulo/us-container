# Pip imports
from tortoise import fields, models


class Tax(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    rate = fields.DecimalField(max_digits=10, decimal_places=6)
    state = fields.TextField()
    account = fields.ForeignKeyField("models.Account", related_name="tax", index=True)

    class PydanticMeta:
        exclude = [
            "account",
        ]

    class Meta:
        table = "tax"

    def __str__(self):
        return f"{self.state}"
