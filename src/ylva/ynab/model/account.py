from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class Account(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    name: str
    type_: str = field(metadata=field_options(alias="type"))
    on_budget: bool
    closed: bool
    note: str
    balance: float
    cleared_balance: float
    uncleared_balance: float
    transfer_payee_id: str
    direct_import_linked: bool
    direct_import_in_error: bool
    deleted: bool
