# Pip imports
from tortoise import fields, models


class OrderAddress(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    street_address = fields.TextField(null=True)
    zip = fields.TextField(null=True)
    state = fields.TextField(null=True)
    city = fields.TextField(null=True)
    county = fields.TextField(null=True)

    class PydanticMeta:
        exclude = ["created_at", "modified_at"]
        computed = ("full_address",)

    def full_address(self) -> str:
        if self.city is None or self.state is None or self.zip is None:
            return ""
        street_address = self.street_address + "," if self.street_address else ""
        return f"{street_address} {self.city}, {self.state} {self.zip}"

    class Meta:
        table = "order_address"
