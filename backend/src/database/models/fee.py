# Pip imports
from tortoise import fields, models
from decimal import Decimal
from typing import Optional
from tortoise.exceptions import NoValuesFetched

# Internal imports
from src.database.models.orders.fee_type import FeeType


class Fee(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    fee_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    fee_type = fields.CharEnumField(FeeType, max_length=50, null=True)
    due_at = fields.DatetimeField(null=True)
    order = fields.ForeignKeyField("models.Order", related_name="fees", index=True)
    type = fields.ForeignKeyField(
        "models.FeeType", related_name="fees", index=True, null=True
    )  # TODO SET THIS BACK TO NOT NULL ONCE MIGRATION IS COMPETE
    class PydanticMeta:
        computed = [
            "calculated_is_taxable",
            "calculated_remaining_balance",
        ]
        exclude = [
            "modified_at",
            "order",
        ]
    class Meta:
        table = "fee"

    def __str__(self):
        return f"{self.fee_type}: {self.fee_amount}, {self.due_at}"

    def calculated_is_taxable(self) -> Optional[bool]:
        try:
            if hasattr(self.type, 'is_taxable') and self.type.is_taxable == True:
                return True
            else:
                return False
        except NoValuesFetched:
            return False

    def calculated_remaining_balance(self) -> Optional[Decimal]:
        try:
            if not self.fee_balance:
                return Decimal(0)
            most_recent_balance = max(self.fee_balance, key=lambda x: x.created_at)
            return most_recent_balance.remaining_balance
        except :
            return 0
