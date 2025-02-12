# Pip imports
from tortoise import fields, models


class AuthManagementToken(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    token = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="auth_management_token")

    class Meta:
        table = "auth_management_token"
