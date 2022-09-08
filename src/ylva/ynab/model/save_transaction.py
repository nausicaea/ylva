import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional, Set

from mashumaro import DataClassDictMixin

from . import Id
from .transaction import Transaction
from .transaction_status import TransactionStatus

_LOG: logging.Logger = logging.getLogger(__name__)
MAX_MEMO_LENGTH: int = 200


@dataclass
class Builder:
    t: Transaction
    payee_id: Optional[str] = field(default=None)
    payee_name: Optional[str] = field(default=None)
    category_id: Optional[str] = field(default=None)
    approved: Optional[bool] = field(default=None)

    def with_payee_id(self, i: str) -> "Builder":
        self.payee_id = i
        return self

    def with_payee_name(self, n: str) -> "Builder":
        self.payee_name = n
        return self

    def with_category_id(self, i: str) -> "Builder":
        self.category_id = i
        return self

    def with_approval(self, a: bool) -> "Builder":
        self.approved = a
        return self

    def build(self) -> "SaveTransaction":
        if self.t.memo is not None and len(self.t.memo) > MAX_MEMO_LENGTH:
            memo = self.t.memo
        else:
            memo = None

        st = SaveTransaction(
            self.t.id_,
            self.t.account_id,
            self.t.date,
            self.t.amount,
            payee_id=self.payee_id,
            payee_name=self.payee_name,
            category_id=self.category_id,
            approved=self.approved,
            memo=memo,
        )
        return st


@dataclass
class SaveTransaction(DataClassDictMixin):
    id_: Id

    account_id: str
    date: date
    amount: int
    payee_id: Optional[str] = field(default=None)
    payee_name: Optional[str] = field(default=None)
    category_id: Optional[str] = field(default=None)
    memo: Optional[str] = field(default=None)
    cleared: Optional[TransactionStatus] = field(default=None)
    approved: Optional[bool] = field(default=None)
    flag_color: Optional[str] = field(default=None)
    import_id: Optional[str] = field(default=None)
    # subtransactions: Optional[List[SaveSubtransaction]]

    @classmethod
    def builder(cls, t: Transaction) -> Builder:
        return Builder(t)

    def __pre_serialize__(self) -> "SaveTransaction":
        if self.memo is not None and len(self.memo) > MAX_MEMO_LENGTH:
            _LOG.warning(
                f"Transaction {self.id_} ({self.date.isoformat()}; {self.amount / 1000}) memo will be "
                f"truncated to {MAX_MEMO_LENGTH} characters"
            )
            self.memo = self.memo[:MAX_MEMO_LENGTH]

        return self

    def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        d.pop("id_")

        none_value_keys: Set[str] = set()
        for k, v in d.items():
            if v is None:
                none_value_keys.add(k)

        for k in none_value_keys:
            d.pop(k)

        return d
