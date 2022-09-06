import logging
from enum import Flag

from .ynab.model.transaction import Transaction
from .ynab.model.transaction_status import TransactionStatus

_LOG: logging.Logger = logging.getLogger(__name__)


class TFilter(Flag):
    NONE = 0b00000
    TRANSFER = 0b00001
    RECONCILED = 0b00010
    ASSIGNED_PAYEE = 0b00100
    ASSIGNED_CATEGORY = 0b01000
    ASSIGNED_MEMO = 0b10000
    ALL = TRANSFER | RECONCILED | ASSIGNED_PAYEE | ASSIGNED_CATEGORY | ASSIGNED_MEMO


def predicate_transaction(t: Transaction, f: TFilter) -> bool:
    if TFilter.TRANSFER in f:
        if t.transfer_transaction_id is None:
            return False
    else:
        if t.transfer_transaction_id is not None:
            return False

    if TFilter.RECONCILED in f:
        if t.cleared is not TransactionStatus.RECONCILED:
            return False
    else:
        if t.cleared is TransactionStatus.RECONCILED:
            return False

    if TFilter.ASSIGNED_PAYEE in f:
        if t.payee_id is None:
            return False
    else:
        if t.payee_id is not None:
            return False

    if TFilter.ASSIGNED_CATEGORY in f:
        if t.category_id is None:
            return False
    else:
        if t.category_id is not None:
            return False

    if TFilter.ASSIGNED_MEMO in f:
        if t.memo is None or len(t.memo) > 200:
            return False
    else:
        if t.memo is not None:
            return False

    return True
