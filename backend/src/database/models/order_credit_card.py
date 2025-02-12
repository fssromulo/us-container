# Pip imports
from tortoise import fields, models

# Internal imports
from src.database.models.card_merchants import CardMerchants
from src.database.models.card_types import CardTypes


class OrderCreditCard(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    card_type = fields.CharEnumField(CardTypes, null=True)
    merchant_name = fields.CharEnumField(CardMerchants, null=True)
    response_from_gateway = fields.JSONField(null=True)
    order = fields.ForeignKeyField("models.Order", related_name="credit_card")

    class PydanticMeta:
        # Let's exclude the created timestamp
        exclude = [
            "order.order_commission",
            "order_commission",
            "account",
        ]

    class Meta:
        table = "order_credit_card"
