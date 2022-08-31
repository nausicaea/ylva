from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.account import Account


@dataclass
class AccountsList(DataClassDictMixin):
    accounts: List[Account]
    server_knowledge: int


@dataclass
class AccountsResponse(ResponseWrapper[AccountsList], DataClassJSONMixin):
    pass


@dataclass
class Params(ParamsBuilder):
    last_knowledge_of_server: Optional[int] = field(default=None)

    def with_last_knowledge_of_server(self, n: int) -> "Params":
        self.last_knowledge_of_server = n
        return self

    def build(self) -> Optional[Dict[str, str]]:
        if self.last_knowledge_of_server is not None:
            return {"last_knowledge_of_server": str(self.last_knowledge_of_server)}
        else:
            return None


@dataclass
class ListAccounts(ApiEndpoint):
    budget_id: str

    def params(self) -> ParamsBuilder:
        return Params()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/accounts"

    def response_data_type(self) -> Type[AccountsResponse]:
        return AccountsResponse

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
