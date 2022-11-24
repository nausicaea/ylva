from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from mashumaro import DataClassDictMixin, field_options

from . import Id
from .scheduled_subtransaction import ScheduledSubtransaction


@dataclass
class ScheduledTransaction(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    date_first: date
    date_next: date
    frequency: str
    amount: int
    memo: Optional[str]
    flag_color: str
    account_id: Id
    payee_id: Optional[Id]
    category_id: Optional[Id]
    transfer_account_id: Optional[Id]
    deleted: bool
    account_name: str
    payee_name: Optional[str]
    category_name: Optional[str]
    subtransactions: List[ScheduledSubtransaction]
