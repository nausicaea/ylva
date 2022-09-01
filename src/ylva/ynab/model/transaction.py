from dataclasses import dataclass, field
from datetime import date
from typing import List

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import DataClassJSONMixin

from ylva.ynab.model.subtransaction import Subtransaction
from ylva.ynab.model.transaction_status import TransactionStatus


@dataclass
class Transaction(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    date: date
    amount: int
    memo: str
    cleared: TransactionStatus
    approved: bool
    flag_color: str
    account_id: str
    payee_id: str
    category_id: str
    transfer_account_id: str
    transfer_transaction_id: str
    matched_transaction_id: str
    import_id: str
    deleted: bool
    account_name: str
    payee_name: str
    category_name: str
    subtransactions: List[Subtransaction]
