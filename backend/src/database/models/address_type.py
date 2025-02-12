# Python imports
from enum import Enum


class AddressType(str, Enum):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    DELIVERY = "DELIVERY"
    SECONDARY = "SECONDAY"
