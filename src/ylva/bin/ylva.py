import logging
from argparse import ArgumentParser, Namespace
from typing import List, Optional, cast

from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from ..config import Config
from ..convert_ntn_to_iti import convert_ntn_to_iti
from ..get_api_token import get_api_token
from ..list_transactions import list_transactions
from ..transaction_filter import TFilter, predicate_transaction
from ..ynab.model.save_transaction import SaveTransaction
from ..ynab.model.transaction_status import TransactionStatus
from ..ynab.payees.list import ListPayees, PayeesResponse
from ..ynab.transactions.list import TransactionType
from ..ynab.transactions.update import (SaveTransactionWrapper,
                                        UpdateTransaction)
from . import DEFAULT_CONFIG_FILE, start

_LOG: logging.Logger = logging.getLogger(f"{__package__}.ylva")


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
        payees, _ = await client.get(ListPayees(budget_id))
        if payees is None:
            return

        transactions = await list_transactions(
            client, budget_id, TransactionType.UNCATEGORIZED
        )
        if transactions is None:
            return

        update_queue: List[SaveTransaction] = list()
        f = TFilter.NO_TRANSFER | TFilter.ASSIGNED_MEMO
        for t in transactions.data.transactions:
            if not predicate_transaction(t, f):
                continue

            for payee in cast(PayeesResponse, payees).data.payees:
                if payee.deleted:
                    continue
                elif t.memo is not None and payee.name.lower() in t.memo.lower():
                    _LOG.info(
                        f"MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was matched to payee {payee.name}"
                    )
                    st = SaveTransaction(
                        t.id_,
                        t.account_id,
                        t.date,
                        t.amount,
                        payee_id=payee.id_,
                        payee_name=payee.name,
                    )
                    update_queue.append(st)
            else:
                _LOG.warning(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was not matched to a payee"
                )

        for t in update_queue:
            tw = SaveTransactionWrapper(t)
            _LOG.info(
                f"UPDATING: Transaction {t.id_} ({t.date} - {t.amount}) with new payee information"
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
        payment_to_category = await convert_ntn_to_iti(
            client, budget_id, config.payment_to_category
        )

        transactions = await list_transactions(
            client, budget_id, TransactionType.UNCATEGORIZED
        )
        if transactions is None:
            return

        update_queue: List[SaveTransaction] = list()
        for t in transactions.data.transactions:
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
            elif t.category_id is not None:
                _LOG.debug(
                    f"SKIPPING: Transaction {t.id_}  ({t.date} - {t.amount}) has an assigned category"
                )
                continue
            elif t.payee_id is None:
                _LOG.warning(
                    f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has no payee, so I cannot find the "
                    "appropriate category "
                )
                continue
            elif t.memo is not None and len(t.memo) > 200:
                _LOG.warning(
                    f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has a memo over 200 characters. YNAB will "
                    "complain when updating this transaction "
                )
                continue

            if t.payee_id in payment_to_category.keys():
                ci = payment_to_category[t.payee_id]

                _LOG.info(
                    f"MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was matched to category {ci}"
                )
                st = SaveTransaction(
                    t.id_,
                    t.account_id,
                    t.date,
                    t.amount,
                    category_id=ci,
                )
                update_queue.append(st)
            else:
                _LOG.warning(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount}) was not matched to a category"
                )

        for t in update_queue:
            tw = SaveTransactionWrapper(t)
            _LOG.info(
                f"UPDATING: Transaction {t.id_} ({t.date} - {t.amount}) with new category information"
            )

            if not dry_run:
                await client.put(UpdateTransaction(budget_id, t.id_), tw)


async def approve(matches: Namespace, config: Config) -> None:
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
        transactions = await list_transactions(
            client, budget_id, TransactionType.UNCATEGORIZED
        )
        if transactions is None:
            return

        update_queue: List[SaveTransaction] = list()
        for t in transactions.data.transactions:
            pass

    raise NotImplementedError()


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

    await matches.func(matches, config)


if __name__ == "__main__":
    main()
