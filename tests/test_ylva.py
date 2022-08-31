from typing import Generic, List, Type, TypeVar

import mt940
import pytest
import reidun.client
from reidun.auth_method import BearerAuth
from reidun.endpoint import ApiEndpoint, ParamsBuilder
from reidun.serialization import PermissiveSchema, SerializableData
from swagger_client.api.budgets_api import BudgetsApi
from swagger_client.api_client import ApiClient

from ylva import __version__

_TOKEN: str = "***REMOVED***"


T = TypeVar("T", bound=SerializableData)


@dataclass
class BudgetsEntry(SerializableData):
    pass


@dataclass
class Budgets(SerializableData):
    budgets: List[BudgetsEntry]


class ResponseWrapper(SerializableData, Generic[T]):
    class ResponseWrapperSchema(MSchema):
        data = fields.Nested(T.Schema)

    data: T
    Schema: Type[MSchema] = ResponseWrapperSchema


class ListBudgets(ApiEndpoint):
    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return "/v1/budgets"

    def response_data_type(self) -> Type[ResponseWrapper[Budgets]]:
        return ResponseWrapper[Budgets]

    def request_data_type(self) -> Type[SerializableData]:
        raise NotImplementedError()


def test_version():
    assert __version__ == "0.1.0"


def test_load_mt940() -> None:
    with open(
        "/Users/young0000/Downloads/finances/lohnkonto-20220401-20220823-mt940.sta"
    ) as f:
        data = mt940.parse(f)
        print(data)


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_get_budgets() -> None:
    client = ApiClient(header_name="Authorization", header_value=f"Bearer {_TOKEN}")
    budgets_api = BudgetsApi(api_client=client)
    data = budgets_api.get_budgets()
    print(data)


@pytest.mark.asyncio
async def test_create_client() -> None:
    async with reidun.client.ApiClient(
        "https://api.youneedabudget.com", auth=BearerAuth(_TOKEN)
    ) as client:
        data = await client.get(ListBudgets())
        print(data)
