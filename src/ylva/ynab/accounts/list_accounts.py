from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from mashumaro import DataClassDictMixin, field_options
from mashumaro.helper import field_options
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from ylva.ynab import ResponseWrapper


@dataclass
class AccountsEntry(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    name: str
    type_: str = field(metadata=field_options(alias="type"))
    on_budget: bool
    closed: bool
    note: str
    balance: float
    cleared_balance: float
    uncleared_balance: float
    transfer_payee_id: str
    direct_import_linked: bool
    direct_import_in_error: bool
    deleted: bool


@dataclass
class AccountsList(DataClassDictMixin):
    accounts: List[AccountsEntry]
    server_knowledge: int


@dataclass
class Accounts(ResponseWrapper[AccountsList], DataClassJSONMixin):
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

    def response_data_type(self) -> Type[Accounts]:
        return Accounts

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
