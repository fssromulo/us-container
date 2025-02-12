# Pip imports
from tortoise import fields, models


class OrderCommision(models.Model):
    id = fields.UUIDField(pk=True)
    display_order_id = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    is_team_commission = fields.BooleanField(default=False)
    paid_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    delivered_at = fields.DatetimeField(null=True)
    sub_total_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True)
    total_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True)
    profit = fields.DecimalField(max_digits=10, decimal_places=4, null=True)
    is_team_lead = fields.BooleanField(null=True)
    team_lead = fields.ForeignKeyField("models.User", related_name="team_lead_commission", null=True, index=True)
    managing_agent = fields.ForeignKeyField(
        "models.User", related_name="managing_agent_commission", null=True, index=True
    )
    agent = fields.ForeignKeyField("models.User", related_name="agent_commission", null=True, index=True)
    can_see_profit = fields.BooleanField(default=True)
    account = fields.ForeignKeyField("models.Account", related_name="order_commission", index=True)
    total_commission = fields.DecimalField(max_digits=10, decimal_places=4, null=True)
    manager_commission_owed = fields.DecimalField(max_digits=10, decimal_places=4, null=True)
    agent_commission_owed = fields.DecimalField(max_digits=10, decimal_places=4, null=True)

    class PydanticMeta:
        exclude = ["account", "user", "order"]

    class Meta:
        table = "order_commission"

    def __str__(self):
        return f"{self.display_order_id}"
