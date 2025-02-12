# Pip imports
from tortoise import fields, models


class TeamMember(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    team_member = fields.OneToOneField("models.User", related_name="team_member", index=True)
    team_lead = fields.ForeignKeyField("models.User", related_name="team_lead", index=True)

    class Meta:
        table = "team_member"

    class PydanticMeta:
        exclude = [
            "team_lead.manager",
            "team_member.assistant",
            "team_member.team_member",
            "team_member.team_lead",
            "team_lead.assistant",
            "team_lead.team_member",
            "team_lead.team_lead",
        ]
