from enum import Enum


class FeeType(str, Enum):
    LATE = "LATE"
    CREDIT_CARD = "CREDIT_CARD"
    RUSH = "RUSH"
    FIRST_PAYMENT = "FIRST_PAYMENT"
