from dataclasses import dataclass, field
from typing import Optional

from mashumaro import DataClassDictMixin, field_options


@dataclass
class Memo(DataClassDictMixin):
    creditor_ref: Optional[str] = field(metadata=field_options(alias="CdtrRef"))
    unstructured: Optional[str] = field(metadata=field_options(alias="Ustrd"))
    additional_transaction_info: Optional[str] = field(
        metadata=field_options(alias="AddtlNtryInf")
    )
