# Pip imports
from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)
    # change this back to auto add
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    email = fields.CharField(unique=True, max_length=255)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    display_name = fields.CharField(max_length=50, null=True)
    is_active = fields.BooleanField(default=True)
    phone = fields.CharField(max_length=50, null=True)
    role_id = fields.TextField(null=True)
    preferences = fields.JSONField(null=True)
    rental_preferences = fields.JSONField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="users", index=True)
    birthday = fields.DateField(null=True)
    shirt_size = fields.TextField(null=True)
    team_leader = fields.ForeignKeyField("models.User", null=True)
    mailing_address = fields.TextField(null=True)

    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return ""

    class PydanticMeta:
        exclude = [
            "account",
            "order",
            "note",
            "agent_commission",
            "team_lead_commission",
            "managing_agent_commission",
            "quote_search",
            "transactions",
        ]
        computed = ["full_name"]
        allow_cycles = True
        backward_relations = True

    class Meta:
        table = "users"
