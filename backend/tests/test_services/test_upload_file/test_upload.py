# Python imports
from textwrap import dedent
from typing import Generator

# Pip imports
import pytest
from botocore.errorfactory import ClientError
from faker import Faker
from fastapi import status

# Internal imports
from src.config import settings
from src.services.upload_file.signer import b64_decode, force_unicode
from src.services.upload_file.upload import UploadHelper, format_filename


fake = Faker()


def test_from_filename(s3: Generator):
    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")

    formatted_filename = format_filename(filename)
    upload_helper = UploadHelper()
    _name = upload_helper.from_filename(filename)
    assert _name.key_name.split("/")[-1] == formatted_filename
    assert len(_name.key_name.split("/")[-2]) == 28


def test_from_id(s3: Generator):
    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")

    upload_helper = UploadHelper()
    upload_helper = upload_helper.from_filename(filename)

    _id = upload_helper.get_id()
    _name = upload_helper.get_name()
    from_id = upload_helper.from_id(_id=_id)
    assert from_id.key_name == _name


def test_from_id_failure(s3: Generator):
    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")

    upload_helper = UploadHelper()
    upload_helper = upload_helper.from_filename(filename)

    _id = dedent(
        """dXBsb2Fkcy85Ny9jMi84ZjNjMDNlZTQ0ZDk4NTRjOGFkYzJlNDdmNjdlL2ZhaW
    wtaW1hZ2UuanBnOjVvdTRJeTNqcWhFT3JpN2UwYXBBTnRnb3o0dw"""
    )
    from_id = upload_helper.from_id(_id=_id)
    assert from_id is None


def test_exists_file(s3: Generator):
    upload_helper = UploadHelper(key_name="test_mock_image.jpg")
    response = upload_helper.exists(s3_bucket_name="mock-bucket")
    assert response.get("ResponseMetadata", {}).get("HTTPStatusCode") == status.HTTP_200_OK


def test_not_exists_file(s3: Generator):
    upload_helper = UploadHelper(key_name="image.jpg")
    with pytest.raises(ClientError):
        upload_helper.exists(s3_bucket_name="mock-bucket")


@pytest.mark.parametrize(
    "value, result",
    [
        ("img1-front.jpg", True),
        ("foto-ground.jpeg", True),
        ("foto-right-side.png", True),
        ("foto-left-side.bmp", False),
        ("foto-back.exe", False),
        ("foto-top", False),
    ],
)
def test_is_extension_valid(value: str, result: bool, s3: Generator):
    upload_helper = UploadHelper(value)
    _id = upload_helper.get_id()
    upload_helper = upload_helper.from_id(_id)
    assert upload_helper.is_extension_valid() is result


def test_get_name(s3: Generator):
    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")

    upload_helper = UploadHelper()
    upload_helper = upload_helper.from_filename(filename)
    _name = upload_helper.get_name()
    assert _name == upload_helper.key_name


def test_get_id(s3: Generator):
    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")

    upload_helper = UploadHelper()
    upload_helper = upload_helper.from_filename(filename)

    _id = upload_helper.get_id()
    decoded_id = force_unicode(b64_decode(_id.encode("ascii")))
    file_id, sign = decoded_id.split(":")
    assert file_id == upload_helper.key_name
    assert len(sign) == 27


def test_get_request(s3: Generator, monkeypatch):
    monkeypatch.setattr(settings, "AWS_S3_BUCKET_NAME", "mock-bucket")
    monkeypatch.setattr(settings, "AWS_DEFAULT_ACL", "public-read")

    data = {"filename": fake.file_name(extension="jpg"), "content-type": "image/jpeg"}
    filename = data.get("filename", "")
    content_type = data.get("content-type", "")

    upload_helper = UploadHelper()
    upload_helper = upload_helper.from_filename(filename)

    request = upload_helper.get_presigned_post_url(max_size=1024 * 1024 * 10, content_type=content_type)
    assert settings.AWS_S3_BUCKET_NAME in request["url"]
    assert data["content-type"] == request["fields"]["Content-Type"]
    assert settings.AWS_DEFAULT_ACL == request["fields"]["acl"]
    assert "AWSAccessKeyId" in request["fields"].keys()
    assert upload_helper.key_name == request["fields"]["key"]
    assert "policy" in request["fields"].keys()
    assert "signature" in request["fields"].keys()
