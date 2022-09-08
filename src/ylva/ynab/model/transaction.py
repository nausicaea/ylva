import logging
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from mashumaro import DataClassDictMixin, field_options

from .subtransaction import Subtransaction
from .transaction_status import TransactionStatus

_LOG: logging.Logger = logging.getLogger(__name__)
MAX_MEMO_LENGTH: int = 200


@dataclass
class Transaction(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    date: date
    amount: int
    memo: Optional[str]
    cleared: TransactionStatus
    approved: bool
    flag_color: str
    account_id: str
    payee_id: Optional[str]
    category_id: Optional[str]
    transfer_account_id: Optional[str]
    transfer_transaction_id: Optional[str]
    matched_transaction_id: Optional[str]
    import_id: Optional[str]
    deleted: bool
    account_name: str
    payee_name: Optional[str]
    category_name: Optional[str]
    subtransactions: List[Subtransaction]

    def __pre_serialize__(self) -> "Transaction":
        if self.memo is not None and len(self.memo) > MAX_MEMO_LENGTH:
            _LOG.warning(
                f"Transaction {self.id_} ({self.date.isoformat()}; {self.amount / 1000}) memo will be "
                f"truncated to {MAX_MEMO_LENGTH}"
            )
            self.memo = self.memo[:MAX_MEMO_LENGTH]

        return self
