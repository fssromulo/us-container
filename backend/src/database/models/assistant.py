# Python imports

# Pip imports
from tortoise import fields, models


class Assistant(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    assistant = fields.OneToOneField("models.User", related_name="assistant", index=True)
    manager = fields.ForeignKeyField("models.User", related_name="manager", index=True)

    class Meta:
        table = "assistant"

    class PydanticMeta:
        exclude = [
            "assistant.team_member",
            "assistant.team_lead",
            "manager.assistant",
            "manager.team_member",
            "manager.team_lead",
            "manager.manager",
        ]
