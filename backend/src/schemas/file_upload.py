# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseConfig, BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.file_upload import FileUpload


# from src.database.models.file_upload_folder_type import FileUploadFolderType


class Config(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


FileUploadInSchema = pydantic_model_creator(
    FileUpload,
    name="FileUploadIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)
FileUpdateInSchema = pydantic_model_creator(
    FileUpload,
    name="FileUploadIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

FileUploadOutSchema = pydantic_model_creator(FileUpload, name="FileUploadOut", exclude=("order", "account", "other_product"))


class RequestFields(BaseModel):
    AWSAccessKeyId: str
    acl: str
    content_type: Optional[str]
    key: str
    policy: str
    signature: str


class RequestSchema(BaseModel):
    url: str
    fields: RequestFields


class PresignedUrlInfo(BaseModel):
    request: RequestSchema
    id: str


class CreateFileUpload(BaseModel):
    file_name: Optional[str]
    content_type: Optional[str]
    folder_type: Optional[str]
    account_id: Optional[int]
    order_id: Optional[str]
    other_product_id: Optional[str]


class GetS3Object(BaseModel):
    bucket_name: Optional[str]
    object_name: Optional[str]
    folder_type: Optional[str]
    account_id: Optional[int]
    order_id: Optional[str]
    other_product_id: Optional[str]
