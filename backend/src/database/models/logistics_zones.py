# Pip imports
from tortoise import fields, models


class LogisticsZones(models.Model):
    id = fields.UUIDField(pk=True)
    account_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now_add=True)
    zone_name = fields.TextField()
    support_number = fields.CharField(50, null=True)
    direct_number = fields.CharField(50, null=True)
    coordinator_name = fields.TextField(null=True)
    email = fields.TextField(null=True)
    color = fields.TextField(null=True)
    
    class Meta:
        table = "logistics_zones"

