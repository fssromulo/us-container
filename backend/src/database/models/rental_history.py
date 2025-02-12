# Pip imports
from tortoise import fields, models


class RentalHistory(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    rent_started_at = fields.DatetimeField(null=True)  # delivered_at from order
    rent_ended_at = fields.DatetimeField(null=True)  # whatever date they gave you in the csv
    line_item = fields.ForeignKeyField("models.LineItem", related_name="rental_history", index=True)
    inventory = fields.ForeignKeyField(
        "models.ContainerInventory", related_name="rental_history", index=True, null=True
    )

    class Meta:
        table = "rental_history"

    def __str__(self):
        return f"{self.notes}"
