# Python imports
import base64

# Pip imports
from jwt.utils import base64url_encode, force_bytes

# Internal imports
from src.services.upload_file import signer


def test_salted_hmac() -> None:
    _hash = "src.services.upload_file.signer.Signer"
    value = "test_signer"
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a"
    response = signer.salted_hmac(_hash, value, secret)
    salted_decode = base64.urlsafe_b64encode((response.digest())).strip(b"=").decode()
    assert response.hexdigest() == "e44c760253e0e6120d0e9d4bd7dce14881b0a2b0"
    assert response.name == "hmac-sha1"
    assert response.block_size == 64
    assert response.blocksize == 64
    assert response.digest_size == 20
    assert response.digest() == b"\xe4Lv\x02S\xe0\xe6\x12\r\x0e\x9dK\xd7\xdc\xe1H\x81\xb0\xa2\xb0"
    assert salted_decode == "5Ex2AlPg5hINDp1L19zhSIGworA"


def test_b64_encode() -> None:
    secret = b"82bc6b0c9b7f4cf5910117ab8db2e87a"
    response = signer.b64_encode(secret)
    assert response == base64.b64encode(secret).split(b"=")[0]


def test_b64_decode() -> None:
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a:test"
    signed_hash = base64url_encode(force_bytes(signer.Signer().sign(secret)))
    signed_hash = signed_hash.decode("utf-8")
    signed_hash = signer.force_unicode(signer.b64_decode(signed_hash.encode("ascii")))
    response = signed_hash.split(":")
    assert response[0] == secret.split(":")[0]
    assert response[1] == secret.split(":")[1]


def test_constant_time_compare() -> None:
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a"
    signed_hash = signer._base64_hmac("src.services.upload_file.signer.Signer" + "signer", secret, None)
    secret_sign = signer.Signer().signature(secret)

    signer_true = signer.constant_time_compare(signed_hash, secret_sign)
    assert signer_true is True

    signer_false = signer.constant_time_compare("abc", secret_sign)
    assert signer_false is False


def test_base64_hmac() -> None:
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a"
    encrypt = signer.b64_encode(signer.salted_hmac("abc", secret, "key").digest())
    response = signer._base64_hmac("abc", secret, "key")
    assert response == encrypt.decode()
    assert response is not None


def test_signer_sign_unsign() -> None:
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a"
    response = signer.Signer().sign(secret)
    assert signer.Signer().unsign(response) == secret


def test_signer_sign_unsign_failure() -> None:
    secret = "82bc6b0c9b7f4cf5910117ab8db2e87a"
    response = signer.Signer().sign(secret + "abc")
    assert signer.Signer().unsign(response) != secret
