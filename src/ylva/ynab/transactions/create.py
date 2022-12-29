from collections.abc import Sized
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Type

from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model import Id
from ..model.save_transaction import SaveTransaction
from ..model.transaction import Transaction


@dataclass
class _SaveTransactionsResponse(DataClassDictMixin):
    server_knowledge: int
    transaction_ids: List[Id] = field(default_factory=list)
    transaction: Optional[Transaction] = field(default=None)
    transactions: List[Transaction] = field(default_factory=list)
    duplicate_import_ids: List[Id] = field(default_factory=list)


@dataclass
class SaveTransactionsResponse(
    ResponseWrapper[_SaveTransactionsResponse], DataClassJSONMixin
):
    pass


@dataclass
class SaveTransactionsWrapper(DataClassJSONMixin):
    transaction: Optional[SaveTransaction]
    transactions: List[SaveTransaction]

    def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        none_value_keys: Set[str] = set()
        for k, v in d.items():
            if v is None:
                none_value_keys.add(k)
            elif isinstance(v, Sized) and len(v) == 0:
                none_value_keys.add(k)

        for k in none_value_keys:
            d.pop(k)

        return d


@dataclass
class CreateTransactions(ApiEndpoint):
    budget_id: str

    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/transactions/import"

    def response_data_type(self) -> Type[SaveTransactionsResponse]:
        return SaveTransactionsResponse

    def request_data_type(self) -> Type[SaveTransactionsWrapper]:
        return SaveTransactionsWrapper
