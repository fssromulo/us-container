from enum import Enum


class PaymentOptions(str, Enum):
    CC = "CC"
    ECheck = "Echeck"
    Check = "Check"
    Financed = "Financed"
    Wire = "Wire"
    RTO = "RTO"
    Leased = "Leased"
    Lease = "Lease"
    Zelle = "Zelle"
    Cash = "Cash"
    ECheck_ACH = "Echeck (ACH On File)"
    ECheck_Record = "Echeck (Record Payment)"
    CC_Record = "CC (Record transaction)"
