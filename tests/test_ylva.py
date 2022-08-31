import pytest
from reidun.client import ApiClient

from ylva import __version__
from ylva.ynab.accounts.list_accounts import Accounts, ListAccounts
from ylva.ynab.budgets.list_budgets import Budgets, ListBudgets
from ylva.ynab.payees.list_payees import ListPayees, Payees
from ylva.ynab.transactions.list_transactions import (ListTransactions,
                                                      Transactions)
from ylva.ynab.transactions.update_transaction import (Transaction,
                                                       UpdateTransaction)


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
    assert isinstance(data, Payees)


@pytest.mark.asyncio
async def test_list_accounts(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListAccounts(ynab_default_budget))
    assert isinstance(data, Accounts)


@pytest.mark.asyncio
async def test_list_transactions(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListTransactions(ynab_default_budget))
    print(data.data.transactions[-1])
    assert isinstance(data, Transactions)
