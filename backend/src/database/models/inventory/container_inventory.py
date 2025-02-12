# Pip imports
from tortoise import fields

# Internal imports
from src.database.models.inventory.inventory import Inventory


class ContainerInventory(Inventory):
    container_number = fields.TextField(null=True)
    container_release_number = fields.TextField(null=True)
    product = fields.ForeignKeyField("models.ContainerProduct", related_name="container_inventory", null=True)
    vendor = fields.ForeignKeyField("models.Vendor", related_name="container_inventory", null=True)
    account = fields.ForeignKeyField(
        "models.Account",
        related_name="container_inventory",
    )
    depot = fields.ForeignKeyField("models.Depot", related_name="container_inventory", null=True)
    container_color = fields.TextField(null=True)
    image_urls = fields.JSONField(null=True)
    metadata = fields.JSONField(null=True)
    description = fields.TextField(null=True)
    revenue = fields.DecimalField(max_digits=10, decimal_places=2,null=True)

    class Meta:
        table = "container_inventory"

    class PydanticMeta:
        exclude = [
            "account",
        ]
