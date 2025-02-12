# Python imports
from enum import Enum


class WelcomeCallStatus(str, Enum):
    YES = "YES"
    NO = "NO"
    IN_PROGRESS = "IN_PROGRESS"
