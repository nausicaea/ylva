from dataclasses import dataclass, field
from typing import List, Optional, Type

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model import Id
from ..model.transaction import Transaction
from ..model.update_transaction import UpdateTransaction


@dataclass
class SaveTransactionsWrapper(DataClassDictMixin):
    server_knowledge: int
    transaction_ids: List[Id] = field(default_factory=list)
    transaction: Optional[Transaction] = field(default=None)
    transactions: List[Transaction] = field(default_factory=list)
    duplicate_import_ids: List[Id] = field(default_factory=list)


@dataclass
class SaveTransactionsResponse(
    ResponseWrapper[SaveTransactionsWrapper], DataClassJSONMixin
):
    pass


@dataclass
class UpdateTransactionsWrapper(DataClassJSONMixin):
    transactions: List[UpdateTransaction]


@dataclass
class UpdateMultipleTransactions(ApiEndpoint):
    budget_id: str

    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/transactions"

    def response_data_type(self) -> Type[SaveTransactionsResponse]:
        return SaveTransactionsResponse

    def request_data_type(self) -> Type[UpdateTransactionsWrapper]:
        return UpdateTransactionsWrapper
