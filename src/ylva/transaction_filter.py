import logging
from enum import Flag, auto

from .ynab.model.transaction import Transaction
from .ynab.model.transaction_status import TransactionStatus

_LOG: logging.Logger = logging.getLogger(__name__)


class TFilter(Flag):
    TRANSFER = auto()
    NO_TRANSFER = auto()
    RECONCILED = auto()
    NOT_RECONCILED = auto()
    ASSIGNED_PAYEE = auto()
    NO_PAYEE = auto()
    ASSIGNED_CATEGORY = auto()
    NO_CATEGORY = auto()
    ASSIGNED_MEMO = auto()
    NO_MEMO = auto()


def predicate_transaction(t: Transaction, f: TFilter) -> bool:
    failures = [
        TFilter.TRANSFER in f and t.transfer_transaction_id is None,
        TFilter.NO_TRANSFER in f and t.transfer_transaction_id is not None,
        TFilter.RECONCILED in f and t.cleared is not TransactionStatus.RECONCILED,
        TFilter.NOT_RECONCILED in f and t.cleared is TransactionStatus.RECONCILED,
        TFilter.ASSIGNED_PAYEE in f and t.payee_id is None,
        TFilter.NO_PAYEE in f and t.payee_id is not None,
        TFilter.ASSIGNED_CATEGORY in f and t.category_id is None,
        TFilter.NO_CATEGORY in f and t.category_id is not None,
        TFilter.ASSIGNED_MEMO in f and (t.memo is None or len(t.memo) > 200),
        TFilter.NO_MEMO in f and t.memo is not None,
    ]

    return not any(failures)
