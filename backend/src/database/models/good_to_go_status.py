# Pip imports

# Python imports
from enum import Enum


class GoodToGoStatus(str, Enum):
    YES = "YES"
    NO = "NO"
    IN_PROGRESS = "IN_PROGRESS"
