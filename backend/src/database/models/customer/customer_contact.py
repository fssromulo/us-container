# Pip imports
from tortoise import fields, models


class CustomerContact(models.Model):
    id = fields.UUIDField(pk=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    email = fields.TextField(null=True)
    phone = fields.TextField(null=True)
    customer_address = fields.ForeignKeyField("models.Address")
    customer = fields.ForeignKeyField("models.Customer", related_name="customer_contacts", index=True)
    account = fields.ForeignKeyField("models.Account")
    created_at = fields.DatetimeField(auto_now_add=True, null=True)
    modified_at = fields.DatetimeField(auto_now=True, null=True)

    class Meta:
        table = "customer_contact"

    class PydanticMeta:
        exclude = ["account"]
