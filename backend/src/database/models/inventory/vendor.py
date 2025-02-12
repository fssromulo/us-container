# Pip imports
from tortoise import fields, models


class Vendor(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    name = fields.TextField(null=True)
    address = fields.TextField(null=True)
    city = fields.TextField(null=True)
    state = fields.TextField(null=True)
    zip = fields.TextField(null=True)
    primary_phone = fields.TextField(null=True)
    primary_email = fields.CharField(max_length=255, null=True)
    secondary_phone = fields.TextField(null=True)
    secondary_email = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="vendor", index=True)
    country = fields.TextField(null=True)
    country_code_primary = fields.TextField(null=True)
    country_code_secondary = fields.TextField(null=True)
    type = fields.ForeignKeyField("models.VendorType", related_name="vendor", index=True, null=True)

    class Meta:
        table = "vendor"

    class PydanticMeta:
        exclude = [
            "account",
            "inventory",
            "inventory",
            "container_inventory",
            "other_inventory",
            "container_depot",
            "note",
        ]

    def __str__(self):
        return f"{self.name}"
