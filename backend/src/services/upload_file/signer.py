# Python imports
import base64
import hashlib
import hmac
import re
import secrets
from typing import Union

# Pip imports
from jwt.utils import force_bytes
from six import binary_type, text_type

# Internal imports
from src.config import settings


_SEP_UNSAFE = re.compile(r"^[A-z0-9-_=]*$", 0)


class BadSignature(Exception):
    """Signature does not match."""

    pass


class InvalidAlgorithm(ValueError):
    """Algorithm is not supported by hashlib."""

    pass


def salted_hmac(key_salt: str, value: str, secret: str = None, *, algorithm: str = "sha1") -> hmac.HMAC:
    """Return the HMAC of "value", using a key generated from key_salt and a secret.
    :param key_salt: The key salt
    :param value: The value to hash
    :param secret: The secret key
    :param algorithm: The hashing algorithm
    :return: The HMAC
    """
    if secret is None:
        secret = settings.SECRET_KEY

    key_salt = force_bytes(key_salt)
    secret = force_bytes(secret)
    try:
        hasher = getattr(hashlib, algorithm)
    except AttributeError as e:
        raise InvalidAlgorithm(f"{algorithm} is not an algorithm accepted by the hashlib module.") from e

    key = hasher(key_salt + secret).digest()
    return hmac.new(key, msg=force_bytes(value), digestmod=hasher)


def b64_encode(s: bytes) -> bytes:
    """Base64 encode a bytestring.
    :param s: The bytestring to encode
    :return: The encoded bytestring
    """
    return base64.urlsafe_b64encode(s).strip(b"=")


def b64_decode(s: bytes) -> bytes:
    """Base64 decode a bytestring.
    :param s: The bytestring to decode
    :return: The decoded bytestring
    """
    pad = b"=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def constant_time_compare(val1: str, val2: str) -> bool:
    """Return True if the two strings are equal, False otherwise.
    :param val1: The first value
    :param val2: The second value
    :return: True if the two strings are equal, False otherwise
    """
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))


def _base64_hmac(salt: str, value: str, key: str = None) -> str:
    """Return a base64 encoded HMAC value.
    :param salt: The salt
    :param value: The value to hash
    :param key: The secret key
    :return: The base64 encoded HMAC value
    """
    return b64_encode(salted_hmac(salt, value, key).digest()).decode()


def force_unicode(value: Union[bytes, str]) -> str:
    """Converts a string argument to a unicode string.
    :param value: The value to convert
    :return: The converted value
    """
    if isinstance(value, binary_type):
        return value.decode("utf-8")
    elif isinstance(value, text_type):
        return value
    raise TypeError("Expected a string value")


class Signer:
    """Signer class."""

    def __init__(self, key: str = None, sep: str = ":", salt: str = None) -> None:
        """Initialize the Signer.
        :param key: The secret key
        :param sep: The separator
        :param salt: The salt
        """
        self.key = key
        self.sep = sep
        if _SEP_UNSAFE.match(self.sep):
            raise ValueError(f"Unsafe Signer separator: {sep} (cannot be empty or consist of only A-z0-9-_=)")
        self.salt = salt or f"{self.__class__.__module__}.{self.__class__.__name__}"

    def signature(self, value: str) -> str:
        """Return the signature for the given value.
        :param value: The value to sign
        :return: The signature
        """
        return _base64_hmac(f"{self.salt}signer", value, self.key)

    def sign(self, value: str) -> str:
        """Sign the given value.
        :param value: The value to sign
        :return: The signed value
        """
        return f"{value}{self.sep}{self.signature(value)}"

    def unsign(self, signed_value: str) -> str:
        """Unsign the given value.
        :param signed_value: The signed value
        :return: The unsigned value
        """
        if self.sep not in signed_value:
            raise Exception(f"No '{self.sep}' found in value")

        value, sig = signed_value.rsplit(self.sep, 1)
        if constant_time_compare(sig, self.signature(value)):
            return value

        raise BadSignature(f"Signature '{sig}' does not match")
