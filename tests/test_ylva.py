import pytest
from reidun.client import ApiClient

from ylva import __version__
from ylva.ynab.budgets.budgets import Budgets
from ylva.ynab.budgets.list_budgets import ListBudgets


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_list_budgets(ynab_api_client: ApiClient) -> None:
    data, _ = await ynab_api_client.get(ListBudgets())
    assert isinstance(data, Budgets)


# @pytest.mark.asyncio
# async def test_list_payees(ynab_personal_api_token: str) -> None:
#     async with reidun.client.ApiClient(
#         "https://api.youneedabudget.com", auth=BearerAuth(ynab_personal_api_token)
#     ) as client:
#         data, _ = await client.get(ListPayees())
#         print(data)
