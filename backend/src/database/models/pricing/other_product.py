# Pip imports
from tortoise import fields

# Internal imports
from src.database.models.pricing.product import Product


class OtherProduct(Product):
    shipping_time = fields.TextField(null=True)
    product_link = fields.TextField(null=True)
    in_stock = fields.BooleanField(default=True)
    account = fields.ForeignKeyField("models.Account", related_name="account_other_product")

    class Meta:
        table = "other_product"

    class PydanticMeta:
        exclude = [
            "account",
        ]
