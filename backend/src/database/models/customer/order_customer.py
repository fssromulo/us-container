# Pip imports
from tortoise import fields, models


class OrderCustomer(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    street_address = fields.TextField(null=True)
    email = fields.CharField(max_length=255)
    phone = fields.TextField(null=True)
    zip = fields.TextField(null=True)
    state = fields.TextField(null=True)
    city = fields.TextField(null=True)
    county = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account", related_name="customer")
    company_name = fields.TextField(null=True)

    class Meta:
        table = "order_customer"

    def full_name(self) -> str:
        # if self.company_name != '' and self.company_name is not None:
        #     return f"{self.company_name}"
        return f"{self.first_name} {self.last_name}"

    def calculated_name(self) -> str:
        if self.first_name != '' and self.first_name is not None  and self.last_name != '' and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        if self.first_name != '' and self.first_name is not None:
            return f"{self.first_name}"
        if self.last_name != '' and self.last_name is not None:
            return f"{self.last_name}"
        if self.company_name != '' and self.company_name is not None:
            return f"{self.company_name}"
        return ""

    def calculated_full_name(self) -> str:
        if self.first_name != '' and self.first_name is not None  and self.last_name != '' and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        if self.first_name != '' and self.first_name is not None:
            return f"{self.first_name}"
        if self.last_name != '' and self.last_name is not None:
            return f"{self.last_name}"
        return "No name entered"

    class PydanticMeta:
        exclude = [
            "account",
            "order.account",
        ]
        computed = ("full_name", "calculated_name", "calculated_full_name")
        pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
