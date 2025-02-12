# Python imports
import json

# Pip imports
# python imports
import requests

# pip imports
from fastapi import UploadFile
from loguru import logger

# Internal imports
from src.auth.auth import Auth0User
from src.crud.account_crud import account_crud
from src.crud.file_upload_crud import file_upload_crud
from src.crud.line_item_crud import line_item_crud
from src.database.models.account import Account
from src.schemas.file_upload import (
    CreateFileUpload,
    FileUploadInSchema,
    FileUploadOutSchema,
    GetS3Object,
    PresignedUrlInfo,
    RequestFields,
    RequestSchema,
)
from src.services.upload_file.upload import UploadHelper


CONTENT_TYPE = "multipart/form-data"


def create_request_fields_obj(fields_dict: dict) -> RequestFields:
    request_fields_obj = RequestFields(
        AWSAccessKeyId=fields_dict["AWSAccessKeyId"],
        acl=fields_dict["acl"],
        content_type=fields_dict["Content-Type"],
        key=fields_dict["key"],
        policy=fields_dict["policy"],
        signature=fields_dict["signature"],
    )
    return request_fields_obj


async def generate_presigned_post_url(file_data: CreateFileUpload) -> PresignedUrlInfo:
    # Grab objects from the request data
    filename: str = file_data.file_name
    content_type: str = file_data.content_type
    folder_type: str = file_data.folder_type
    order_id: str = file_data.order_id
    other_product_id: str = file_data.other_product_id
    account_id: int = file_data.account_id

    account: Account = await account_crud.get_one(account_id=account_id)
    account_name: str = account.name

    # Get the presigned secure link for them to upload to. This will return all the information we will need for them to make a request for their file
    if order_id is None:
        upload_helper = UploadHelper.from_filename(filename, folder_type, other_product_id, account_name)
    else:
        upload_helper = UploadHelper.from_filename(filename, folder_type, order_id, account_name)

    request = upload_helper.get_presigned_post_url(content_type=content_type, expiration=38000)
    upload_id = upload_helper.get_id()

    # Retrieve that information and store it in a dictionary
    fields_dict = request.get("fields")
    logger.info(fields_dict)
    # Create instances of RequestFields and RequestSchema
    request_fields_obj = create_request_fields_obj(fields_dict)

    request_obj = RequestSchema(url=request.get("url"), fields=request_fields_obj)

    # Build the final upload_object
    upload_object = PresignedUrlInfo(request=request_obj, id=upload_id)

    return upload_object


async def generate_presigned_get_url(s3_file_data: GetS3Object):
    bucket_name: str = s3_file_data.bucket_name
    object_name: str = s3_file_data.object_name
    folder_type: str = s3_file_data.folder_type
    order_id: str = s3_file_data.order_id
    other_product_id: str = s3_file_data.other_product_id
    account_id: int = s3_file_data.account_id

    account: Account = await account_crud.get_one(account_id=account_id)
    account_name: str = account.name

    # this takes the object name and sets the key name which is the name of the object
    if order_id is None:
        upload_helper = UploadHelper.from_filename(object_name, folder_type, other_product_id, account_name)
    else:
        upload_helper = UploadHelper.from_filename(object_name, folder_type, order_id, account_name)

    request = upload_helper.get_presigned_get_url(bucket_name=bucket_name)
    return request


async def create_file_upload(file_upload_data: FileUploadInSchema):
    try:
        saved_file_upload: FileUploadOutSchema = await file_upload_crud.create(file_upload_data)
        return saved_file_upload
    except Exception as e:
        logger.info(f"There was an issue creating the file upload object: {e}")
        raise e
    # return saved_file_upload


async def update_file_upload(id, file_upload_data: FileUploadInSchema):
    try:
        saved_file_upload: FileUploadOutSchema = await file_upload_crud.update(
            file_upload_data.account_id, id, file_upload_data
        )
        return saved_file_upload
    except Exception as e:
        logger.info(f"There was an issue updating the file upload object: {e}")
        raise e
    # return saved_file_upload


async def delete_file_upload(file_id: str, account_id: str):
    try:
        # Check if image is used already
        line_item_used = await line_item_crud.db_model.filter(file_upload_id=file_id).count()
        if line_item_used == 0:
            return await file_upload_crud.delete_one(account_id, file_id)
    except Exception as e:
        logger.info(f"There was an issue deleting the file object: {e}")
        raise e
