# Pip imports
from tortoise import fields, models


class OrderContract(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    status = fields.TextField()
    contract_id = fields.TextField()
    meta_data = fields.JSONField(null=True)
    contract_pdf_link = fields.TextField(null=True)
    order = fields.ForeignKeyField("models.Order", related_name="order_contract", index=True)

    class Meta:
        table = "order_contract"

    def __str__(self):
        return f"{self.order.id}: {self.status}"
