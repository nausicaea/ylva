from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Type

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.transaction import Transaction


@dataclass
class TransactionsList(DataClassDictMixin):
    transactions: List[Transaction]
    server_knowledge: int


@dataclass
class TransactionsResponse(ResponseWrapper[TransactionsList], DataClassJSONMixin):
    pass


class TransactionType(Enum):
    UNCATEGORIZED = "uncategorized"
    UNAPPROVED = "unapproved"


@dataclass
class Params(ParamsBuilder):
    last_knowledge_of_server: Optional[int] = field(default=None)
    since_date: Optional[date] = field(default=None)
    type_: Optional[TransactionType] = field(default=None)

    def with_last_knowledge_of_server(self, n: int) -> "Params":
        self.last_knowledge_of_server = n
        return self

    def with_since_date(self, d: date) -> "Params":
        self.since_date = d
        return self

    def with_type(self, t: TransactionType) -> "Params":
        self.type_ = t
        return self

    def build(self) -> Optional[Dict[str, str]]:
        params: Dict[str, str] = {}
        if self.last_knowledge_of_server is not None:
            params["last_knowledge_of_server"] = str(self.last_knowledge_of_server)
        if self.since_date is not None:
            params["since_date"] = self.since_date.isoformat()
        if self.type_ is not None:
            params["type"] = str(self.type_.value)

        if len(params) == 0:
            return None
        else:
            return params


@dataclass
class ListTransactions(ApiEndpoint):
    budget_id: str

    def params(self) -> Params:
        return Params()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/transactions"

    def response_data_type(self) -> Type[TransactionsResponse]:
        return TransactionsResponse

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
