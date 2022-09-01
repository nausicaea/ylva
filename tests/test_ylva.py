import logging
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, cast

import pytest
from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import DataClassJSONMixin
from reidun.client import ApiClient

from ylva import __version__
from ylva.ynab.accounts.list import AccountsResponse, ListAccounts
from ylva.ynab.budgets.list import BudgetsResponse, ListBudgets
from ylva.ynab.model.transaction import Transaction
from ylva.ynab.model.transaction_status import TransactionStatus
from ylva.ynab.payees.list import ListPayees, PayeesResponse
from ylva.ynab.transactions.list import (ListTransactions,
                                         TransactionsResponse, TransactionType)
from ylva.ynab.transactions.update import UpdateTransaction

_LOG: logging.Logger = logging.getLogger(__name__)


@dataclass
class SaveTransaction(DataClassDictMixin):
    account_id: str
    date: date
    amount: int
    payee_id: Optional[str] = field(
        default=None, metadata=field_options(serialization_strategy=ABCD)
    )
    payee_name: Optional[str] = field(default=None)
    category_id: Optional[str] = field(default=None)
    memo: Optional[str] = field(default=None)
    cleared: Optional[TransactionStatus] = field(default=None)
    approved: Optional[bool] = field(default=None)
    flag_color: Optional[str] = field(default=None)
    import_id: Optional[str] = field(default=None)
    # subtransactions: Optional[List[SaveSubtransaction]]


@dataclass
class TransactionRequestData(DataClassJSONMixin):
    transaction: SaveTransaction


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_list_budgets(ynab_api_client: ApiClient) -> None:
    data, _ = await ynab_api_client.get(ListBudgets())
    assert isinstance(data, BudgetsResponse)


@pytest.mark.asyncio
async def test_list_payees(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListPayees(ynab_default_budget))
    assert isinstance(data, PayeesResponse)


@pytest.mark.asyncio
async def test_list_accounts(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListAccounts(ynab_default_budget))
    assert isinstance(data, AccountsResponse)


@pytest.mark.asyncio
async def test_list_transactions(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    data, _ = await ynab_api_client.get(ListTransactions(ynab_default_budget))
    assert isinstance(data, TransactionsResponse)


@pytest.mark.asyncio
async def test_payee_matching(
    ynab_api_client: ApiClient, ynab_default_budget: str
) -> None:
    payees, _ = await ynab_api_client.get(ListPayees(ynab_default_budget))
    if payees is None:
        return

    lt = ListTransactions(ynab_default_budget)
    ltp = lt.params().with_type(TransactionType.UNCATEGORIZED).build()
    transactions, _ = await ynab_api_client.get(lt, params=ltp)
    if transactions is None:
        return

    update_queue: List[Transaction] = list()
    for t in cast(TransactionsResponse, transactions).data.transactions:
        if t.transfer_transaction_id is not None:
            _LOG.debug(
                f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) is a transfer"
            )
            continue
        elif t.cleared is TransactionStatus.RECONCILED:
            _LOG.debug(
                f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has been reconciled"
            )
            continue
        elif t.approved:
            _LOG.debug(
                f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has been approved"
            )
            continue
        elif t.payee_id is not None or t.category_id is not None:
            _LOG.debug(
                f"SKIPPING: Transaction {t.id_}  ({t.date} - {t.amount}) has an assigned payee and/or category"
            )
            continue
        elif t.memo is None:
            _LOG.warning(
                f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has no memo, so I cannot find the appropriate payee and category"
            )
            continue

        for payee in cast(PayeesResponse, payees).data.payees:
            if payee.deleted:
                continue
            elif payee.name in t.memo:
                _LOG.info(
                    f"MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was matched to payee {payee.name}"
                )
                t.payee_id = payee.id_
                t.payee_name = payee.name
                update_queue.append(t)
        else:
            _LOG.warning(
                f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was not matched to a payee"
            )

        for t in update_queue:
            tw = TransactionRequestData(t)
            data, _ = await ynab_api_client.put(
                UpdateTransaction(ynab_default_budget, t.id_), data=tw
            )
            pass
