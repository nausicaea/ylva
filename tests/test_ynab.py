import pytest
from reidun.client import ApiClient

from ylva.ynab.accounts.list import AccountsResponse, ListAccounts
from ylva.ynab.budgets.list import BudgetsResponse, ListBudgets
from ylva.ynab.payees.list import ListPayees, PayeesResponse
from ylva.ynab.transactions.list import ListTransactions, TransactionsResponse


@pytest.mark.asyncio
async def test_list_budgets(ynab_api_client: ApiClient) -> None:
    data, _ = await ynab_api_client.get(ListBudgets())
    assert isinstance(data, BudgetsResponse)


@pytest.mark.asyncio
async def test_list_payees(ynab_api_client: ApiClient, ynab_test_budget: str) -> None:
    data, _ = await ynab_api_client.get(ListPayees(ynab_test_budget))
    assert isinstance(data, PayeesResponse)


@pytest.mark.asyncio
async def test_list_accounts(ynab_api_client: ApiClient, ynab_test_budget: str) -> None:
    data, _ = await ynab_api_client.get(ListAccounts(ynab_test_budget))
    assert isinstance(data, AccountsResponse)


@pytest.mark.asyncio
async def test_list_transactions(
    ynab_api_client: ApiClient, ynab_test_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListTransactions(ynab_test_budget))
    assert isinstance(data, TransactionsResponse)
