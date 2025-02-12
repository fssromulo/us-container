# Pip imports
from tortoise import fields, models


class Country(models.Model):
    id = fields.UUIDField(pk=True)
    country_name = fields.TextField(null=True)
    code = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now_add=True)
    account = fields.ForeignKeyField("models.Account", related_name="country_account")

    class Meta:
        table = "country"

    class PydanticMeta:
        exclude = ["account"]

    def __str__(self):
        return f"{self.id}"
