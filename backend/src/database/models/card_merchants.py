# Python imports
from enum import Enum


class CardMerchants(str, Enum):
    AMEX = "AMEX"
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    DISCOVER = "DISCOVER"
    DINERS = "DINERS"
    JCB = "JCB"
    UNIONPAY = "UNIONPAY"
    MAESTRO = "MAESTRO"
    AMERICAN_EXPRESS = "AMERICANEXPRESS"
    EMPTY = ""
