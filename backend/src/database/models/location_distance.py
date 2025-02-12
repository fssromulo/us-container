# Pip imports
from tortoise import fields, models


class LocationDistances(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    destination_zip = fields.TextField()
    destination_city = fields.TextField()
    origin_zip = fields.TextField()
    distance = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "location_distances"

    def __str__(self):
        return f"{self.distance}"
