from dataclasses import dataclass, field
from typing import Dict, Optional, Type

from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .budgets import Budgets


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
    def params(self) -> ParamsBuilder:
        return Params()

    def path(self) -> str:
        return "/v1/budgets"

    def response_data_type(self) -> Type[Budgets]:
        return Budgets

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
