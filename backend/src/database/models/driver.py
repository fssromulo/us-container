# Pip imports
from tortoise import fields, models


class Driver(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    company_name = fields.TextField(null=True)
    city = fields.TextField(null=True)
    state = fields.TextField(null=True)
    province = fields.TextField(null=True)
    cost_per_mile = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost_per_100_miles = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    phone_number = fields.TextField(null=True)
    email = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="driver")
    is_archived = fields.BooleanField(default=False)
    
    class Meta:
        table = "driver"

    class PydanticMeta:
        exclude = [
            "account",
            "line_item_driver_potential",
            "line_item_driver",
            "deliveries",
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
