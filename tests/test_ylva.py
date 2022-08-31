import pytest
import reidun.client
from reidun.auth_method import BearerAuth

from ylva import __version__
from ylva.ynab.budgets.list_budgets import ListBudgets

_TOKEN: str = "***REMOVED***"


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_list_budgets() -> None:
    async with reidun.client.ApiClient(
        "https://api.youneedabudget.com", auth=BearerAuth(_TOKEN)
    ) as client:
        data, _ = await client.get(ListBudgets())
        print(data)
