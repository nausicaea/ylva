from typing import Optional, cast

from reidun.client import ApiClient

from .ynab.model.transaction import Transaction
from .ynab.transactions.list import (
    ListTransactions,
    TransactionsResponse,
    TransactionType,
)


async def list_transactions(
    client: ApiClient, budget_id: str, t: Optional[TransactionType] = None
) -> list[Transaction]:
    """
    Retrieve a list of transactions from YNAB

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve transactions from
    :param t: an optional filter for transactions
    :raise ValueError: when there are no transactions
    """
    lt = ListTransactions(budget_id)
    if t is not None:
        ltp = lt.params().with_type(t).build()
    else:
        ltp = None
    transactions, _ = await client.get(lt, params=ltp)
    if transactions is not None:
        trns: TransactionsResponse = cast(TransactionsResponse, transactions)
        if len(trns.data.transactions) == 0:
            raise ValueError(f"Budget {budget_id} has no transactions")
        return trns.data.transactions
    else:
        raise ValueError(f"Budget {budget_id} has no transactions")
