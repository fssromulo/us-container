# Pip imports
from tortoise import fields, models


class FixedLocationPrice(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    postal_code = fields.TextField(null=True)
    sale_shipping_price = fields.FloatField(null=True)
    rent_shipping_price = fields.FloatField(null=True)
    size = fields.TextField(null=True)
    location = fields.ForeignKeyField("models.LocationPrice", related_name="fixed_location_prices", null=True)

    class Meta:
        table = "fixed_location_price"

    def __str__(self):
        return f"{self.id}"
