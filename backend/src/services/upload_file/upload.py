# Python imports
import binascii
import mimetypes
import os
import re
from typing import Any, Dict, Union

# Pip imports
import boto3
from botocore.exceptions import ClientError
from jwt.utils import base64url_decode, base64url_encode, force_bytes
from slugify import slugify

# Internal imports
from src.config import settings
from src.crud import file_upload_crud
from src.services.upload_file.signer import BadSignature, Signer, force_unicode


MAX_SIZE = 1024 * 1024 * 10


class BaseUpload:
    """Base class for uploading files to S3"""

    @property
    def s3_client(self) -> boto3.client:
        """Return the S3 client
        :return: The S3 client
        """
        return boto3.client(
            's3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )


def format_filename(filename: str) -> str:
    """Slugify and format a filename
    :param filename: The filename to format
    :return: The formatted filename
    Example:
        >>> format_filename('My File.jpg')
        'my-file.jpg'
    """
    filename = force_unicode(filename)
    name, extension = os.path.splitext(filename)

    name = slugify(name)
    name = re.sub(r'-{2,}', '-', name)

    return f"{name}{extension}"


class UploadHelper(BaseUpload):
    def __init__(self, key_name: str = None) -> None:
        """Initialize the UploadHelper class
        :param key_name: The key name of the file
        """
        self.key_name = key_name

    def get_presigned_post_url(
        self, max_size: int = MAX_SIZE, content_type: str = None, expiration: int = 3600
    ) -> Dict[str, Any]:
        """Generate a presigned post request for uploading files to S3
        :param max_size: Maximum size of the file
        :param content_type: Content type of the file
        :param expiration: Expiration time of the request
        :return: A dictionary containing the request
        Example:
            >>> upload = UploadHelper('uploads/1/2/1234567890.jpg')
            >>> upload.get_presigned_post_url()
            {
                'url': 'https://s3.amazonaws.com/my-bucket',
                'fields': {
                    'Content-Type': 'image/jpeg',
                    'acl': 'public-read',
                    'key': 'uploads/1/2/1234567890.jpg',
                    'AWSAccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                    'policy': 'eyJleHBpcmF0aW9uIjogIjIwMjAtMDMtMjFUMjA6MDA6MDBaIiwgImNvbmRpdGlvbnMiOiBbeyJ...==',
                    'signature': 'BSAMPLEt39SAMPLEFfSAMPLErSAMPLESAMPLESAMPLESAMPLE='
                }
            }
        """
        return self.s3_client.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=self.get_name(),
            Fields={
                'Content-Type': content_type,
                'acl': settings.AWS_DEFAULT_ACL,
            },
            Conditions=[
                {"acl": settings.AWS_DEFAULT_ACL},
                ["content-length-range", 2, max_size],
                {"Content-Type": content_type},
            ],
            ExpiresIn=expiration,
        )

    def get_presigned_get_url(self, bucket_name: str, expiration: int = 30):
        """
        Generate a presigned get URL to share an S3 object

        :param bucket_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        return self.s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": self.key_name}, ExpiresIn=expiration
        )

    def get_id(self) -> str:
        """Return a signed hash of the key name
        :return: A signed hash of the key name
        Example:
            >>> upload = UploadHelper('uploads/1/2/1234567890.jpg')
            >>> upload.get_id()
            'dXBsb2Fkcy8xNi9iOS84ZjA4NWMyZDRlNTZiODBkZDk4NTIxMmU2ZDk4L2ZvdG8tZnJlbnRlLmpwZzpzTnZnTVFCNEstQzI2ejJmNDlELW5tb3BVTzg'
        """
        signed_hash = Signer().sign(self.key_name)
        signed_hash = force_bytes(signed_hash)
        signed_hash = base64url_encode(signed_hash)
        return signed_hash.decode("utf-8")

    def get_name(self) -> str:
        """Return the key name
        :return: The key name
        Example:
            >>> upload = UploadHelper('uploads/1/2/1234567890.jpg')
            >>> upload.get_name()
            'uploads/1/2/1234567890.jpg'
        """
        return self.key_name

    def is_extension_valid(self) -> bool:
        """Check if the extension of the file is valid
        :return: True if the extension is valid, False otherwise
        Example:
            >>> upload = UploadHelper('uploads/1/2/1234567890.jpg')
            >>> upload.is_extension_valid()
            True
        """
        file_type, _ = mimetypes.guess_type(self.key_name)
        extension = mimetypes.guess_extension(file_type) if file_type else None
        return extension in settings.ALLOWED_EXTENSIONS

    def exists(self, s3_bucket_name: str = None) -> Dict[str, Any]:
        """Check if the file exists in S3
        :param s3_bucket_name: The name of the S3 bucket
        :return: A dictionary containing the response
        Example:
            >>> upload = UploadHelper('uploads/1/2/1234567890.jpg')
            >>> upload.exists()
            {
                'AcceptRanges': 'bytes',
                'LastModified': datetime.datetime(2020, 3, 21, 20, 0, 0, tzinfo=tzutc()),
                'ContentLength': 1234567890,
                'ETag': '"1234567890abcdef1234567890abcdef"',
                'ContentType': 'image/jpeg',
                'Metadata': {}
            }
        """
        if not s3_bucket_name:
            s3_bucket_name = settings.AWS_S3_BUCKET_NAME
        try:
            response = self.s3_client.head_object(Bucket=s3_bucket_name, Key=self.key_name)
        except ClientError as e:
            raise e
        return response

    @classmethod
    def from_id(cls, _id: str) -> Union[None, 'UploadHelper']:
        """Checks if an id is valid for uploading the file to S3
        :param _id: The id of the file
        :return: An UploadHelper object if the id is valid, None otherwise
        Example:
            >>> upload = UploadHelper.from_id('dXBsb2Fk0cy8xNi9iOS84ZjA4NWMyZDRlNTZiODBkZDk4NTIxMmU...')
            >>> upload.get_name()
            'uploads/1/2/1234567890.jpg'
        """
        signed_hash = force_unicode(_id)
        try:
            signed_hash = base64url_decode(signed_hash)
        except binascii.Error:
            return None

        try:
            _hash = Signer().unsign(force_unicode(signed_hash))
        except BadSignature:
            return None

        return cls(_hash)

    @classmethod
    def from_filename(cls, filename: str, folder_type: str, item_id: str, account_name: str) -> 'UploadHelper':
        """Returns a specific name for the 'path' file
        :param filename: The name of the file
        :param folder_type: This folder reflects the kind of file that is being sent up
        :param order_id: This is the order id that is associated with the file that is being sent up
        :param account_name: This is the name of the account that is having the file submitted
        :return: An UploadHelper object
        Example:
            >>> upload = UploadHelper.from_filename('foo.jpg')
            >>> upload.get_name()
            'uploads/1/2/1234567890.jpg'
        """
        # it will go uploads/{account}/{cc_front/cc_back/dl_front/dl_back}/{order_id}/file
        filename = format_filename(filename)
        file_upload_crud.file_upload_crud
        key_parts = [account_name, item_id, folder_type, filename]
        key_name = 'uploads/' + '/'.join(key_parts)
        return cls(key_name=key_name)
