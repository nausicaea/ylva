from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Generic, List, Optional, Type, TypeVar

import mt940
import pytest
import reidun.client
from mashumaro.helper import field_options
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.auth_method import BearerAuth
from reidun.endpoint import ApiEndpoint, ParamsBuilder

from ylva import __version__

_TOKEN: str = "***REMOVED***"


T = TypeVar("T")


@dataclass
class DateFormat(DataClassJSONMixin):
    format_: str = field(metadata=field_options(alias="format"))


@dataclass
class CurrencyFormat(DataClassJSONMixin):
    iso_code: str
    example_format: str
    decimal_digits: int
    decimal_separator: str
    symbol_first: bool
    group_separator: str
    currency_symbol: str
    display_symbol: bool


@dataclass
class BudgetAccountsEntry(DataClassJSONMixin):
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
class BudgetsEntry(DataClassJSONMixin):
    id_: str = field(metadata=field_options(alias="id"))
    name: str
    last_modified_on: datetime
    first_month: date
    last_month: date
    date_format: DateFormat
    currency_format: CurrencyFormat
    accounts: Optional[List[BudgetAccountsEntry]] = field(default=None)


@dataclass
class BudgetsList(DataClassJSONMixin):
    budgets: List[BudgetsEntry]
    default_budget: Optional[BudgetsEntry]


@dataclass
class ResponseWrapper(Generic[T]):
    data: T


@dataclass
class Budgets(ResponseWrapper[BudgetsList], DataClassJSONMixin):
    pass


class ListBudgets(ApiEndpoint):
    def params(self) -> ParamsBuilder:
        raise NotImplementedError()

    def path(self) -> str:
        return "/v1/budgets"

    def response_data_type(self) -> Type[Budgets]:
        return Budgets

    def request_data_type(self) -> Type[DataClassJSONMixin]:
        raise NotImplementedError()


def test_version():
    assert __version__ == "0.1.0"


def test_load_mt940() -> None:
    with open(
        "/Users/young0000/Downloads/finances/lohnkonto-20220401-20220823-mt940.sta"
    ) as f:
        data = mt940.parse(f)
        print(data)


@pytest.mark.asyncio
async def test_create_client() -> None:
    async with reidun.client.ApiClient(
        "https://api.youneedabudget.com", auth=BearerAuth(_TOKEN)
    ) as client:
        data, _ = await client.get(ListBudgets())
        print(data)
