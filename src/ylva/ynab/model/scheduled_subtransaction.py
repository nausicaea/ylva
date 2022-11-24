from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class ScheduledSubtransaction(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    scheduled_transaction_id: Id
    amount: float
    memo: str
    payee_id: Id
    category_id: Id
    transfer_account_id: Id
    deleted: bool
