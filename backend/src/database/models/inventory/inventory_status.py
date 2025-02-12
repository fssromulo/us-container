from enum import Enum


class InventoryStatus(str, Enum):
    ATTACHED = "Attached"
    AVAILABLE = "Available"
    IN_LINE = "In Line"
    DELIVERED = "Delivered"
    UNKNOWN = "UNKNOWN"
    Ready = "Ready"
