from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from mashumaro import DataClassDictMixin, field_options

from . import Id
from .subtransaction import Subtransaction
from .transaction_status import TransactionStatus


@dataclass
class Transaction(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    date: date
    amount: int
    memo: Optional[str]
    cleared: TransactionStatus
    approved: bool
    flag_color: str
    account_id: Id
    payee_id: Optional[Id]
    category_id: Optional[Id]
    transfer_account_id: Optional[Id]
    transfer_transaction_id: Optional[Id]
    matched_transaction_id: Optional[Id]
    import_id: Optional[Id]
    deleted: bool
    account_name: str
    payee_name: Optional[str]
    category_name: Optional[str]
    subtransactions: List[Subtransaction]
