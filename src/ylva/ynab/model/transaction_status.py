from enum import Enum


class TransactionStatus(Enum):
    UNCLEARED = "uncleared"
    CLEARED = "cleared"
    RECONCILED = "reconciled"
