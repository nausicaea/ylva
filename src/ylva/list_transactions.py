from typing import Optional, cast

from reidun.client import ApiClient

from .ynab.transactions.list import (ListTransactions, TransactionsResponse,
                                     TransactionType)


async def list_transactions(
    client: ApiClient, budget_id: str, t: Optional[TransactionType] = None
) -> Optional[TransactionsResponse]:
    """
    Retrieve a list of transactions from YNAB

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve transactions from
    :param t: an optional filter for transactions
    """
    lt = ListTransactions(budget_id)
    if t is not None:
        ltp = lt.params().with_type(t).build()
    else:
        ltp = None
    transactions, _ = await client.get(lt, params=ltp)
    if transactions is not None:
        return cast(TransactionsResponse, transactions)
    else:
        return None
