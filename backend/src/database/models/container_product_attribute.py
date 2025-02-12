# Pip imports
from tortoise import fields, models


class ContainerProductAttribute(models.Model):
    id = fields.UUIDField(pk=True)
    container_attribute = fields.ForeignKeyField(
        "models.ContainerAttribute", related_name="container_product_attributes", null=True, index=True
    )
    container_product_new = fields.ForeignKeyField(
        "models.ContainerProduct", related_name="container_product_attributes", null=True, index=True
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        table = "container_product_attribute"
