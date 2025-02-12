# Python imports
from enum import Enum


class CardTypes(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    EMPTY = ""
