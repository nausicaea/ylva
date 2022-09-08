import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Optional

from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from .. import DEFAULT_CONFIG_FILE
from ..config import Config
from ..convert_ntn_to_iti import convert_ntn_to_iti
from ..get_api_token import get_api_token
from ..list_payees import list_payees
from ..list_transactions import list_transactions
from ..transaction_filter import TFilter, predicate_transaction
from ..ynab.model.payee import Payee
from ..ynab.model.save_transaction import SaveTransaction
from ..ynab.model.transaction import Transaction
from ..ynab.model.transaction_status import TransactionStatus
from ..ynab.transactions.list import TransactionType
from ..ynab.transactions.update import (SaveTransactionWrapper,
                                        UpdateTransaction)
from . import start

_LOG: logging.Logger = logging.getLogger(f"{__package__}.ylva")


async def _payee_wrapper(client: ApiClient, budget_id: str) -> list[Payee]:
    try:
        return await list_payees(client, budget_id)
    except ValueError as ex:
        _LOG.exception("Failed to retrieve payees", exc_info=ex)
        print(ex.args[0])
        sys.exit(1)


async def _transaction_wrapper(
    client: ApiClient, budget_id: str, tt: TransactionType | None = None
) -> list[Transaction]:
    try:
        return await list_transactions(client, budget_id, tt)
    except ValueError as ex:
        _LOG.exception("Failed to retrieve transactions", exc_info=ex)
        print(ex.args[0])
        sys.exit(1)


async def _conversion_wrapper(
    client: ApiClient, budget_id: str, ntn: Dict[str, str]
) -> Dict[str, str]:
    try:
        return await convert_ntn_to_iti(client, budget_id, ntn)
    except ValueError as ex:
        _LOG.exception("Failed to convert the payee-category-mapping", exc_info=ex)
        print(ex.args[0])
        sys.exit(1)


async def assign_payees(matches: Namespace, config: Config) -> None:
    dry_run: bool = matches.dry_run
    rate_limit: Optional[float] = config.rate_limit
    api_url: str = config.api_url
    api_token: str = await get_api_token(config)
    budget_id: str = config.budget_id

    async with ApiClient(
        api_url,
        auth=BearerAuth(api_token),
        rate_limit=rate_limit,
    ) as client:
        payees = await _payee_wrapper(client, budget_id)

        transactions = await _transaction_wrapper(
            client, budget_id, TransactionType.UNAPPROVED
        )

        update_queue: List[SaveTransaction] = list()
        f = (
            TFilter.NOT_RECONCILED
            | TFilter.NO_TRANSFER
            | TFilter.NO_PAYEE
            | TFilter.ASSIGNED_MEMO
        )
        for t in transactions:
            if not predicate_transaction(t, f):
                continue

            assert t.cleared is not TransactionStatus.RECONCILED
            assert t.transfer_transaction_id is None
            assert t.payee_id is None and t.payee_name is None
            assert t.memo is not None

            for payee in payees:
                if payee.deleted:
                    continue
                elif t.memo is not None and payee.name.lower() in t.memo.lower():
                    _LOG.info(
                        f"MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was matched to payee {payee.name}"
                    )
                    st = (
                        SaveTransaction.builder(t)
                        .with_payee_id(payee.id_)
                        .with_payee_name(payee.name)
                        .build()
                    )
                    update_queue.append(st)
            else:
                _LOG.warning(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was not matched to a payee"
                )

        for t in update_queue:
            tw = SaveTransactionWrapper(t)
            _LOG.info(
                f"UPDATING: Transaction {t.id_} ({t.date} - {t.amount / 1000}) with new payee information"
            )

            if not dry_run:
                await client.put(UpdateTransaction(budget_id, t.id_), tw)


async def assign_categories(matches: Namespace, config: Config) -> None:
    dry_run: bool = matches.dry_run
    rate_limit: Optional[float] = config.rate_limit
    api_url: str = config.api_url
    api_token: str = await get_api_token(config)
    budget_id: str = config.budget_id

    async with ApiClient(
        api_url,
        auth=BearerAuth(api_token),
        rate_limit=rate_limit,
    ) as client:
        payment_to_category = await _conversion_wrapper(
            client, budget_id, config.payment_to_category
        )

        transactions = await _transaction_wrapper(
            client, budget_id, TransactionType.UNCATEGORIZED
        )

        update_queue: List[SaveTransaction] = list()
        f = (
            TFilter.NOT_RECONCILED
            | TFilter.NO_TRANSFER
            | TFilter.NO_CATEGORY
            | TFilter.ASSIGNED_PAYEE
        )
        for t in transactions:
            if not predicate_transaction(t, f):
                continue

            assert t.cleared is not TransactionStatus.RECONCILED
            assert t.transfer_transaction_id is None
            assert t.payee_id is not None
            assert t.category_id is None

            if t.payee_id in payment_to_category.keys():
                ci = payment_to_category[t.payee_id]

                _LOG.info(
                    f"MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was matched to category {ci}"
                )
                st = SaveTransaction.builder(t).with_category_id(ci).build()
                update_queue.append(st)
            else:
                _LOG.warning(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was not matched to a category"
                )

        for t in update_queue:
            tw = SaveTransactionWrapper(t)
            _LOG.info(
                f"UPDATING: Transaction {t.id_} ({t.date} - {t.amount / 1000}) with new category information"
            )

            if not dry_run:
                await client.put(UpdateTransaction(budget_id, t.id_), tw)


async def approve(matches: Namespace, config: Config) -> None:
    dry_run: bool = matches.dry_run
    ignore_cleared: bool = matches.ignore_cleared
    ignore_category: bool = matches.ignore_category
    ignore_payee: bool = matches.ignore_payee
    rate_limit: Optional[float] = config.rate_limit
    api_url: str = config.api_url
    api_token: str = await get_api_token(config)
    budget_id: str = config.budget_id

    async with ApiClient(
        api_url,
        auth=BearerAuth(api_token),
        rate_limit=rate_limit,
    ) as client:
        transactions = await _transaction_wrapper(
            client, budget_id, TransactionType.UNAPPROVED
        )

        f: TFilter = TFilter.NOT_RECONCILED | TFilter.NO_TRANSFER
        if not ignore_cleared:
            f |= TFilter.CLEARED
        if not ignore_category:
            f |= TFilter.ASSIGNED_CATEGORY
        if not ignore_payee:
            f |= TFilter.ASSIGNED_PAYEE

        update_queue: List[SaveTransaction] = list()
        for t in transactions:
            if not predicate_transaction(t, f):
                continue

            st = SaveTransaction.builder(t).with_approval(True).build()
            update_queue.append(st)

        for t in update_queue:
            tw = SaveTransactionWrapper(t)
            _LOG.info(
                f"UPDATING: Transaction {t.id_} ({t.date} - {t.amount / 1000}) will be approved"
            )

            if not dry_run:
                await client.put(UpdateTransaction(budget_id, t.id_), tw)


@start
async def main() -> None:
    parser = ArgumentParser(prog="ylva")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
    )
    sub_parsers = parser.add_subparsers(
        required=True,
        dest="root",
        metavar="action",
        description="Choose the budget action",
        help="Choose the budget action",
    )
    approve_parser = sub_parsers.add_parser("approve")
    approve_parser.set_defaults(func=approve)
    approve_parser.add_argument(
        "-s",
        "--ignore-cleared",
        action="store_true",
        help="If set, approve transactions even if they haven't been cleared",
    )
    approve_parser.add_argument(
        "--ignore-category",
        action="store_true",
        help="If set, approve transactions even if they haven't been categorized",
    )
    approve_parser.add_argument(
        "--ignore-payee",
        action="store_true",
        help="If set, approve transactions even if they haven't been assigned a payee",
    )
    assign_parser = sub_parsers.add_parser("assign")
    assign_sub_parsers = assign_parser.add_subparsers(
        required=True,
        dest="assign",
        metavar="destination",
        description="Choose the assignment destination",
        help="Choose the assignment destination",
    )
    payees_parser = assign_sub_parsers.add_parser("payees")
    payees_parser.set_defaults(func=assign_payees)
    categories_parser = assign_sub_parsers.add_parser("categories")
    categories_parser.set_defaults(func=assign_categories)
    matches = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if not DEFAULT_CONFIG_FILE.exists():
        config = Config.create(DEFAULT_CONFIG_FILE)
    else:
        config = Config.load(DEFAULT_CONFIG_FILE)

    if matches.dry_run:
        _LOG.info("Dry-run mode enabled. Not committing any changes")

    await matches.func(matches, config)


if __name__ == "__main__":
    main()
