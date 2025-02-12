# Pip imports
from tortoise import fields, models


class QuoteSearches(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    postal_code = fields.TextField(null=False)
    user = fields.ForeignKeyField("models.User", related_name="quote_search", index=True)
    account = fields.ForeignKeyField("models.Account", related_name="quote_search", index=True)

    class Meta:
        table = "quote_searches"
