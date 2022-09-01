from dataclasses import dataclass
from typing import Type

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from .. import ResponseWrapper
from ..model.save_transaction import SaveTransaction
from ..model.transaction import Transaction


@dataclass
class TransactionWrapper(DataClassDictMixin):
    transaction: Transaction


@dataclass
class TransactionResponse(ResponseWrapper[TransactionWrapper], DataClassJSONMixin):
    pass


@dataclass
class SaveTransactionWrapper(DataClassJSONMixin):
    transaction: SaveTransaction


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

    def request_data_type(self) -> Type[SaveTransactionWrapper]:
        return SaveTransactionWrapper
