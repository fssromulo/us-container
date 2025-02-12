# Pip imports
from tortoise import fields, models


class CustomerApplicationResponse(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    order = fields.ForeignKeyField("models.Order", related_name="application_response")
    customer_application_schema = fields.OneToOneField("models.CustomerApplicationSchema", related_name="customer_application_schema", null=True)
    response_content = fields.JSONField()
    date_accepted = fields.DatetimeField(null=True)
    date_rejected = fields.DatetimeField(null=True)

    class Meta:
        table = "customer_application_response"

    class PydanticMeta:
        exclude = ["order"]
