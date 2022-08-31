import pytest
from reidun.client import ApiClient

from ylva import __version__
from ylva.ynab.budgets.budgets import Budgets
from ylva.ynab.budgets.list_budgets import ListBudgets
from ylva.ynab.payees.list_payees import ListPayees, Payees


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_list_budgets(ynab_api_client: ApiClient) -> None:
    data, _ = await ynab_api_client.get(ListBudgets())
    assert isinstance(data, Budgets)


@pytest.mark.asyncio
async def test_list_payees(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListPayees(ynab_default_budget))
    print(data)
    assert isinstance(data, Payees)
