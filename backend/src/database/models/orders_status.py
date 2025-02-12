# Python imports
from enum import Enum


class OrderStatus(str, Enum):
    ESTIMATE = "Estimate"
    QUOTE = "Quote"
    INVOICED = "Invoiced"
    PAID = "Paid"
    PARTIALLY_PAID = "Partially Paid"
    PURCHASE_ORDER = "Purchase Order"
    DELIVERED = "Delivered"
    COMPLETED = "Completed"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"
    APPROVED = "Approved"
    DELINQUENT = "Delinquent"
    RETURNED = "Returned"
