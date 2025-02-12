# Python imports
from decimal import Decimal
from typing import Optional

# Pip imports
from tortoise import fields, models


class AccessoryLineItem(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    product_type = fields.TextField(null=True)
    other_product_name = fields.TextField(null=True)
    other_product_shipping_time = fields.TextField(null=True)
    line_item = fields.ForeignKeyField("models.LineItem", related_name="accessory_line_item",null=True,blank=True,)
    filename = fields.TextField(null=True)
    content_type = fields.TextField(null=True)
    folder_type = fields.TextField(null=True)
    other_product = fields.ForeignKeyField("models.OtherProduct", related_name="accessory_line_item", index=True, null=True)


    class Meta:
        table = "accessory_line_item"

    def __str__(self):
        return f"{self.id}"
