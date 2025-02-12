# Pip imports
from tortoise import fields, models


class FileUpload(models.Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    filename = fields.TextField()
    content_type = fields.TextField()
    account = fields.ForeignKeyField("models.Account", related_name="file_upload", index=True)
    folder_type = fields.TextField()
    order = fields.ForeignKeyField("models.Order", related_name="file_upload", index=True, null=True)
    other_product = fields.ForeignKeyField("models.OtherProduct", related_name="file_upload", index=True, null=True)

    class PydanticMeta:
        exclude = ["account"]

    class Meta:
        table = "file_upload"
