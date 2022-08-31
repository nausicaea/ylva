from typing import Type

from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .budgets import Budgets


class ListBudgets(ApiEndpoint):
    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return "/v1/budgets"

    def response_data_type(self) -> Type[Budgets]:
        return Budgets

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()
