from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options


@dataclass
class Payee(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    name: str
    transfer_account_id: str
    deleted: bool
