# Pip imports
from tortoise import fields, models


class Customer(models.Model):
    id = fields.UUIDField(pk=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    company_name = fields.TextField(null=True)
    account = fields.ForeignKeyField("models.Account")

    class Meta:
        table = "customer"

    def full_name(self) -> str:
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
