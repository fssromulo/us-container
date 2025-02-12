# Pip imports
from tortoise import fields, models


class ContainerAttribute(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True)
    modified_at = fields.DatetimeField(auto_now=True, null=True)
    name = fields.TextField()
    value = fields.TextField(null=True)

    class Meta:
        table = "container_attribute"

    class PydanticMeta:
        exclude = ["container_product_attributes"]
