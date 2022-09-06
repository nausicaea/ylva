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
    tracker: bool = True

    if TFilter.TRANSFER in f:
        v = t.transfer_transaction_id is not None
        tracker &= v
        _LOG.debug(f"Transaction {t.id_} is a transfer: {v}")
    else:
        tracker &= t.transfer_transaction_id is None

    if TFilter.RECONCILED in f:
        v = t.cleared is TransactionStatus.RECONCILED
        tracker &= v
        _LOG.debug(f"Transaction {t.id_} is reconciled: {v}")
    else:
        tracker &= t.cleared is not TransactionStatus.RECONCILED

    if TFilter.ASSIGNED_PAYEE in f:
        v = t.payee_id is not None
        tracker &= v
        _LOG.debug(f"Transaction {t.id_} has a payee: {v}")
    else:
        tracker &= t.payee_id is None

    if TFilter.ASSIGNED_CATEGORY in f:
        v = t.category_id is not None
        tracker &= v
        _LOG.debug(f"Transaction {t.id_} has a category: {v}")
    else:
        tracker &= t.category_id is None

    if TFilter.ASSIGNED_MEMO in f:
        v = t.memo is not None and len(t.memo) <= 200
        tracker &= v
        _LOG.debug(f"Transaction {t.id_} has a memo: {v}")
    else:
        tracker &= t.memo is None

    return tracker
