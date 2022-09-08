from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class Subtransaction(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    transaction_id: str
    amount: float
    memo: str
    payee_id: str
    payee_name: str
    category_id: str
    category_name: str
    transfer_account_id: str
    transfer_transaction_id: str
    deleted: bool
