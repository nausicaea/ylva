from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional, Set

from mashumaro import DataClassDictMixin

from .transaction_status import TransactionStatus


@dataclass
class SaveTransaction(DataClassDictMixin):
    id_: str

    account_id: str
    date: date
    amount: int
    payee_id: Optional[str] = field(default=None)
    payee_name: Optional[str] = field(default=None)
    category_id: Optional[str] = field(default=None)
    memo: Optional[str] = field(default=None)
    cleared: Optional[TransactionStatus] = field(default=None)
    approved: Optional[bool] = field(default=None)
    flag_color: Optional[str] = field(default=None)
    import_id: Optional[str] = field(default=None)
    # subtransactions: Optional[List[SaveSubtransaction]]

    def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        d.pop("id_")

        none_value_keys: Set[str] = set()
        for k, v in d.items():
            if v is None:
                none_value_keys.add(k)

        for k in none_value_keys:
            d.pop(k)

        return d
