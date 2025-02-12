from enum import Enum


class PurchaseTypes(str, Enum):
    RENT = "RENT"
    RENT_TO_OWN = "RENT_TO_OWN"
    PURCHASE = "PURCHASE"
    PURCHASE_ACCESSORY = "PURCHASE_ACCESSORY"
    ALL = "ALL"
