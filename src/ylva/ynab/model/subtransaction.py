from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class Subtransaction(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    transaction_id: Id
    amount: float
    memo: str
    payee_id: Id
    payee_name: str
    category_id: Id
    category_name: str
    transfer_account_id: Id
    transfer_transaction_id: Id
    deleted: bool
