# Pip imports
from tortoise import fields, models


class InventoryAddress(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    line_item = fields.ForeignKeyField("models.LineItem", related_name="inventory_address", index=True, null=True)
    container_inventory = fields.ForeignKeyField(
        "models.ContainerInventory", related_name="container_inventory_address", index=True, null=True
    )
    other_inventory = fields.ForeignKeyField(
        "models.OtherInventory", related_name="other_inventory_address", index=True, null=True
    )
    address = fields.ForeignKeyField("models.Address", related_name="inventory_address", index=True, null=True)

    class PydanticMeta:
        exclude = [
            "created_at",
            "modified_at",
        ]

        computed = ["full_address_computed"]

    class Meta:
        table = "inventory_address"

    def full_address_computed(self) -> str:
        if hasattr(self.address, "street_address"):
            return (
                self.address.street_address
                + ", "
                + self.address.city
                + ", "
                + self.address.county
                + ", "
                + self.address.state
                + ", "
                + self.address.zip
            )
        else:
            return ""

    def __str__(self):
        return f"{self.id}"
