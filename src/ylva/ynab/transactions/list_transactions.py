from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import Dict, List, Optional, Type

from mashumaro import DataClassDictMixin, field_options
from mashumaro.helper import field_options
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from ylva.ynab import ResponseWrapper


@dataclass
class SubransactionEntry(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
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


@dataclass
class TransactionsEntry(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    date: date
    amount: float
    memo: str
    cleared: str
    approved: bool
    flag_color: str
    account_id: str
    payee_id: str
    category_id: str
    transfer_account_id: str
    transfer_transaction_id: str
    matched_transaction_id: str
    import_id: str
    deleted: bool
    account_name: str
    payee_name: str
    category_name: str
    subtransactions: List[SubransactionEntry]


@dataclass
class TransactionsList(DataClassDictMixin):
    transactions: List[TransactionsEntry]
    server_knowledge: int


@dataclass
class Transactions(ResponseWrapper[TransactionsList], DataClassJSONMixin):
    pass


class TransactionType(Enum):
    UNCATEGORIZED = auto()
    UNAPPROVED = auto()

    def to_str(self) -> str:
        if self is TransactionType.UNCATEGORIZED:
            return "uncategorized"
        elif self is TransactionType.UNAPPROVED:
            return "unapproved"
        else:
            raise ValueError(f"Unrecognized variant of TransactionType: {self}")


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
            params["type"] = self.type_.to_str()

        if len(params) == 0:
            return None
        else:
            return params


@dataclass
class ListTransactions(ApiEndpoint):
    budget_id: str

    def params(self) -> ParamsBuilder:
        return Params()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/transactions"

    def response_data_type(self) -> Type[Transactions]:
        return Transactions

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
