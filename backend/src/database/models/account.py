# Pip imports
from tortoise import fields, models


class Account(models.Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField()
    is_active = fields.BooleanField(default=True)
    cms_attributes = fields.JSONField(null=True)
    auth0_management_token_modified_at = fields.DatetimeField(null=True)
    auth0_management_token = fields.TextField(null=True)
    integrations = fields.JSONField(null=True)
    external_integrations = fields.JSONField(null=True)
    order_status_selection = fields.JSONField(null=True)
    order_status_options = fields.JSONField(null=True)
    pod_contract = fields.TextField(null=True)
    terms_and_conditions = fields.TextField(null=True)
    terms_and_conditions_paid = fields.TextField(default=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = "account"
