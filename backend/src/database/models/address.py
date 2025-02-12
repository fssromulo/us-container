# Python imports

# Pip imports
from tortoise import fields, models

# Internal imports
from src.database.models.address_type import AddressType


class Address(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    street_address = fields.TextField(null=True)
    modified_at = fields.DatetimeField(auto_now=True)
    zip = fields.TextField(null=True)
    state = fields.TextField(null=True)
    city = fields.TextField(null=True)
    county = fields.TextField(null=True)
    type = fields.TextField(null=True)
    latitude = fields.TextField(null=True)
    longitude = fields.TextField(null=True)
    type = fields.CharEnumField(AddressType, null=True)

    class Meta:
        table = "address"

    class PydanticMeta:
        exclude = []
        computed = ["full_address"]

    def full_address(self) -> str:
        if self.city is None or self.state is None or self.zip is None:
            return ""
        street_address = self.street_address + "," if self.street_address else ""
        return f"{street_address} {self.city}, {self.state} {self.zip}"
