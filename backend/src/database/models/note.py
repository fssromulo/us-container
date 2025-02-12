# Pip imports
from tortoise import fields, models


class Note(models.Model):
    id = fields.UUIDField(pk=True)
    title = fields.TextField()
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="note", null=True)
    customer = fields.ForeignKeyField("models.OrderCustomer", related_name="note", null=True, index=True)
    order = fields.ForeignKeyField("models.Order", related_name="note", null=True, index=True)
    line_item = fields.ForeignKeyField("models.LineItem", related_name="note", null=True, index=True)
    inventory = fields.ForeignKeyField("models.ContainerInventory", related_name="note", null=True, index=True)
    depot = fields.ForeignKeyField("models.Depot", related_name="note", null=True, index=True)
    driver = fields.ForeignKeyField("models.Driver", related_name="note", null=True, index=True)
    rental_history = fields.ForeignKeyField("models.RentalHistory", related_name="note", null=True, index=True)
    vendor = fields.ForeignKeyField("models.Vendor", related_name="note", null=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_public = fields.BooleanField(null=True)

    class PydanticMeta:
        # Let's exclude the created timestamp
        exclude = [
            "author.assistant",
            "author.manager",
            "author.team_lead",
            "author.team_member",
            "author.account",
            "author.commission",
            "order",
            "line_item",
            "inventory",
            "depot",
        ]

    class Meta:
        table = "notes"

    def __str__(self):
        return f"{self.title}, {self.author} on {self.created_at}"
