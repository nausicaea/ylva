from typing import Optional, cast

from reidun.client import ApiClient

from .ynab.model.scheduled_transaction import ScheduledTransaction
from .ynab.scheduled_transactions.list import (ListScheduledTransactions,
                                               ScheduledTransactionsResponse)


async def list_scheduled_transactions(
    client: ApiClient, budget_id: str
) -> list[ScheduledTransaction]:
    """
    Retrieve a list of transactions from YNAB

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve transactions from
    :param t: an optional filter for transactions
    """
    lt = ListScheduledTransactions(budget_id)
    transactions, _ = await client.get(lt)

    if transactions is None:
        return list()

    trns: ScheduledTransactionsResponse = cast(
        ScheduledTransactionsResponse, transactions
    )

    return trns.data.scheduled_transactions
