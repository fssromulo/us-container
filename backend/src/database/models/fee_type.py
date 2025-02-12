# Pip imports
from tortoise import fields, models


class FeeType(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField()
    is_taxable = fields.BooleanField(default=False)
    is_archived = fields.BooleanField(default=False)
    is_editable = fields.BooleanField(default=True)
    adjusts_profit = fields.BooleanField(default=True)
    account = fields.ForeignKeyField("models.Account", related_name="account_fee_type", index=True)
    display_name = fields.TextField(null=True)
    line_item_level = fields.BooleanField(default=False)

    class PydanticMeta:
        exclude = [
            "created_at",
            "modified_at",
            "account",
        ]

    class Meta:
        table = "fee_type"

    def __str__(self):
        return f"{self.id}"
