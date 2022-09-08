from typing import cast

from reidun.client import ApiClient

from .ynab.model.payee import Payee
from .ynab.payees.list import ListPayees, PayeesResponse


async def list_payees(client: ApiClient, budget_id: str) -> list[Payee]:
    """
    Retrieve a list of payees from YNAB

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve payees from
    :raise ValueError: when there are no payees
    """
    payees, _ = await client.get(ListPayees(budget_id))
    if payees is not None:
        payees: PayeesResponse = cast(PayeesResponse, payees)
        if len(payees.data.payees) == 0:
            raise ValueError(f"Budget {budget_id} has no payees")
        return payees.data.payees
    else:
        raise ValueError(f"Budget {budget_id} has no payees")
