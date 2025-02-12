# Python imports

# Pip imports
from tortoise import fields, models


# REMOVE unique=True from primary_email after migration
class Depot(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField(null=True)
    street_address = fields.TextField(null=True)
    zip = fields.TextField(null=True)
    primary_email = fields.CharField(max_length=255, null=True)
    secondary_email = fields.TextField(null=True)
    primary_phone = fields.TextField(null=True)
    secondary_phone = fields.TextField(null=True)
    city = fields.TextField(null=True)
    state = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="depot")

    def full_address(self) -> str:
        if self.city is None or self.state is None or self.zip is None:
            return ""
        street_address = self.street_address + "," if self.street_address else ""
        return f"{street_address} {self.city}, {self.state} {self.zip}"

    class Meta:
        table = "depot"

    class PydanticMeta:
        exclude = ["account", "container_inventory", "inventory", "container_depot", "note"]
        computed = ["full_address"]

    def __str__(self):
        return f"{self.name}"
