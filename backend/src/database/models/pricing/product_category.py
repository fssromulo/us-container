# Pip imports
from tortoise import fields, models


class ProductCategory(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        # Let's exclude the created timestamp
        exclude = ["account", "other_product_new"]

    class Meta:
        table = "product_category"
