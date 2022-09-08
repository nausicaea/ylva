from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class Payee(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    name: str
    transfer_account_id: Id
    deleted: bool
