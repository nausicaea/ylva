from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.budget import Budget


@dataclass
class BudgetsList(DataClassDictMixin):
    budgets: List[Budget]
    default_budget: Optional[Budget]


@dataclass
class BudgetsResponse(ResponseWrapper[BudgetsList], DataClassJSONMixin):
    pass


@dataclass
class Params(ParamsBuilder):
    include_accounts: Optional[bool] = field(default=None)

    def with_include_accounts(self, s: bool) -> "Params":
        self.include_accounts = s
        return self

    def build(self) -> Optional[Dict[str, str]]:
        if self.include_accounts is not None:
            return {"include_accounts": str(self.include_accounts)}
        else:
            return None


class ListBudgets(ApiEndpoint):
    def params(self) -> Params:
        return Params()

    def path(self) -> str:
        return "/v1/budgets"

    def response_data_type(self) -> Type[BudgetsResponse]:
        return BudgetsResponse

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
