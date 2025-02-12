# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from tortoise import fields, models


class TransactionType(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    payment_type = fields.CharField(max_length=40)
    order = fields.ForeignKeyField("models.Order", related_name="transaction_type_order", index=True, null=True)
    rent_period = fields.ForeignKeyField(
        "models.RentPeriod", related_name="transaction_type_rent_period", index=True, null=True
    )
    notes = fields.TextField(null=True)
    amount = fields.FloatField(null=True)
    group_id = fields.UUIDField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="transaction_type", index=True)
    credit_card_object = fields.ForeignKeyField("models.OrderCreditCard", related_name="transactions", null=True)
    user = fields.ForeignKeyField("models.User", related_name="transactions", null=True)
    transaction_effective_date = fields.DatetimeField(null=True)
    
    class PydanticMeta:
        exclude = ["modified_at", "order", "account"]

    def calculated_rent_transaction_amount(self) -> Optional[Decimal]:
        if self.rent_period:
            return self.amount
        return Decimal(0)

    class Meta:
        table = "transaction_type"

    def __str__(self):
        return f"{self.id}"
