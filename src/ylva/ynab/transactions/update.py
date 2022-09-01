from dataclasses import dataclass
from typing import Type

from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.transaction import Transaction as Transaction_


@dataclass
class TransactionResponse(ResponseWrapper[Transaction_], DataClassJSONMixin):
    pass


@dataclass
class UpdateTransaction(ApiEndpoint):
    budget_id: str
    transaction_id: str

    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return f"/v1/budgets/{self.budget_id}/transactions/{self.transaction_id}"

    def response_data_type(self) -> Type[TransactionResponse]:
        return TransactionResponse

    def request_data_type(self) -> Type[TransactionResponse]:
        return TransactionResponse
