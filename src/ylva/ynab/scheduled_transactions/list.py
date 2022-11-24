from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.client import ApiEndpoint
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.scheduled_transaction import ScheduledTransaction


@dataclass
class ScheduledTransactionsList(DataClassDictMixin):
    scheduled_transactions: List[ScheduledTransaction]
    server_knowledge: int


@dataclass
class ScheduledTransactionsResponse(
    ResponseWrapper[ScheduledTransactionsList], DataClassJSONMixin
):
    pass


@dataclass
class Params(ParamsBuilder):
    last_knowledge_of_server: Optional[int] = field(default=None)

    def with_last_knowledge_of_server(self, n: int) -> "Params":
        self.last_knowledge_of_server = n
        return self

    def build(self) -> Optional[Dict[str, str]]:
        params: Dict[str, str] = {}
        if self.last_knowledge_of_server is not None:
            params["last_knowledge_of_server"] = str(self.last_knowledge_of_server)

        if len(params) == 0:
            return None
        else:
            return params


@dataclass
class ListScheduledTransactions(ApiEndpoint):
    budget_id: str

    def params(self) -> Params:
        return Params()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/scheduled_transactions"

    def response_data_type(self) -> Type[ScheduledTransactionsResponse]:
        return ScheduledTransactionsResponse

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
