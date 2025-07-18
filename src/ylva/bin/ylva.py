import logging
import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional

from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from ylva.bkb.memo import Memo

from .. import DEFAULT_CONFIG_FILE, week_number
from ..config import Config
from ..conversion import (
    convert_a_to_b,
    convert_ata_to_atb,
    convert_ata_to_btb,
    create_nti_lut,
)
from ..get_api_token import get_api_token
from ..list_categories import list_categories
from ..list_payees import list_payees
from ..list_transactions import list_transactions
from ..transaction_filter import TFilter, predicate_transaction
from ..ynab.model import Id
from ..ynab.model.category import Category
from ..ynab.model.payee import Payee
from ..ynab.model.transaction import Transaction
from ..ynab.model.update_transaction import UpdateTransaction
from ..ynab.transactions.list import TransactionType
from ..ynab.transactions.update_multiple import (
    UpdateMultipleTransactions,
    UpdateTransactionsWrapper,
)
from . import start

_LOG: logging.Logger = logging.getLogger(f"{__package__}.ylva")
_PAYEE_START_INDICATOR: str = "bezugsort:"
_PAYEE_START_OFFSET: int = len(_PAYEE_START_INDICATOR)
_PAYEE_STOP_INDICATOR: str = "transaktionsdatum:"


async def _payee_wrapper(client: ApiClient, budget_id: str) -> list[Payee]:
    try:
        return await list_payees(client, budget_id)
    except ValueError as ex:
        _LOG.exception("Failed to retrieve payees", exc_info=ex)
        print(ex.args[0])
        sys.exit(1)


async def _category_wrapper(client: ApiClient, budget_id: str) -> list[Category]:
    try:
        return await list_categories(client, budget_id)
    except ValueError as ex:
        _LOG.exception("Failed to retrieve categories", exc_info=ex)
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


async def assign_payees(matches: Namespace, config: Config) -> None:
    dry_run: bool = matches.dry_run
    create_payees: bool = matches.create_payees
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

        update_queue: List[UpdateTransaction] = list()
        f = (
            TFilter.NOT_RECONCILED
            | TFilter.NO_TRANSFER
            | TFilter.NO_PAYEE
            | TFilter.ASSIGNED_MEMO
        )
        for t in transactions:
            if not predicate_transaction(t, f):
                continue

            memo_lower = t.memo.lower() if t.memo is not None else None
            for payee in payees:
                if payee.deleted:
                    continue
                elif memo_lower is not None and payee.name.lower() in memo_lower:
                    _LOG.debug(
                        f"MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was matched to payee {payee.name}"
                    )
                    ut = (
                        UpdateTransaction.builder(t)
                        .with_payee_id(payee.id_)
                        .with_payee_name(payee.name)
                        .build()
                    )
                    update_queue.append(ut)
                    break
            else:
                _LOG.debug(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was not matched to a payee"
                )
                if create_payees and t.memo is not None:
                    index_left_brace = t.memo.find("{")
                    index_right_brace = t.memo.rfind("}")

                    if index_left_brace >= 0 and index_left_brace < index_right_brace:
                        probable_json_data = t.memo[index_left_brace:index_right_brace]
                        try:
                            memo_structured = Memo.from_dict(
                                json.loads(probable_json_data)
                            )
                            unstructured_lower = (
                                memo_structured.unstructured.lower()
                                if memo_structured.unstructured is not None
                                else ""
                            )
                            new_payee_start = (
                                unstructured_lower.find(_PAYEE_START_INDICATOR)
                                + _PAYEE_START_OFFSET
                            )
                            new_payee_stop = (
                                unstructured_lower.find(_PAYEE_STOP_INDICATOR) - 1
                            )
                            if memo_structured.unstructured is not None:
                                new_payee_name = memo_structured.unstructured[
                                    new_payee_start:new_payee_stop
                                ].strip()
                                _LOG.info(
                                    f"CREATE: Transaction {t.id_} ({t.date} - {t.amount / 1000}) will receive a new payee: {new_payee_name}"
                                )
                                ut = (
                                    UpdateTransaction.builder(t)
                                    .with_payee_name(new_payee_name)
                                    .build()
                                )
                                update_queue.append(ut)
                        except Exception as ex:
                            _LOG.exception("Failed to parse memo data", exc_info=ex)

        if len(update_queue) > 0:
            _LOG.info(
                f"UPDATING: {len(update_queue)} transactions with new payee information"
            )
            tw = UpdateTransactionsWrapper(update_queue)
            if not dry_run:
                await client.patch(UpdateMultipleTransactions(budget_id), tw)


async def assign_categories(matches: Namespace, config: Config) -> None:
    dry_run: bool = matches.dry_run
    weekwise: bool = matches.weekwise
    filter: Optional[TransactionType] = matches.filter
    force: bool = matches.force
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
        categories = await _category_wrapper(client, budget_id)

        transactions = await _transaction_wrapper(client, budget_id, filter)
        _LOG.info(f"YNAB transmitted {len(transactions)} transactions")

        payee_lut = create_nti_lut(payees)
        category_lut = create_nti_lut(categories)
        payee_to_category = convert_ata_to_btb(
            config.payee_to_category, payee_lut, category_lut
        )

        if weekwise:
            weekwise_payees: list[Id] = convert_a_to_b(
                config.weekwise_payees, payee_lut
            )
            week_no_to_category: dict[int, Id] = convert_ata_to_atb(
                config.week_no_to_category, category_lut
            )
        else:
            weekwise_payees = list()
            week_no_to_category = dict()

        update_queue: List[UpdateTransaction] = list()
        if force:
            f = TFilter.NO_TRANSFER | TFilter.ASSIGNED_PAYEE
        else:
            f = (
                TFilter.NOT_RECONCILED
                | TFilter.NO_TRANSFER
                | TFilter.NO_CATEGORY
                | TFilter.ASSIGNED_PAYEE
            )

        transactions = [t for t in transactions if predicate_transaction(t, f)]
        _LOG.info(f"Categorizing {len(transactions)} transactions")

        for t in transactions:
            if t.payee_id is not None:
                if t.payee_id in payee_to_category.keys():
                    ci = payee_to_category[t.payee_id]
                    _LOG.debug(
                        f"MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was matched to category {ci}"
                    )
                    ut = UpdateTransaction.builder(t).with_category_id(ci).build()
                    update_queue.append(ut)
                elif weekwise and t.payee_id in weekwise_payees:
                    week_no = week_number(t.date)
                    ci = week_no_to_category[week_no]
                    _LOG.debug(
                        f"MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was matched to week {week_no} and thus to category {ci}"
                    )
                    ut = UpdateTransaction.builder(t).with_category_id(ci).build()
                    update_queue.append(ut)
            else:
                _LOG.info(
                    f"NO MATCH: Transaction {t.id_} ({t.date} - {t.amount / 1000}) was not matched to a category"
                )

        if len(update_queue) > 0:
            _LOG.info(
                f"UPDATING: {len(update_queue)} transactions with new category information"
            )
            tw = UpdateTransactionsWrapper(update_queue)
            if not dry_run:
                await client.patch(UpdateMultipleTransactions(budget_id), tw)


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

        update_queue: List[UpdateTransaction] = list()
        for t in transactions:
            if not predicate_transaction(t, f):
                continue

            ut = UpdateTransaction.builder(t).with_approval(True).build()
            update_queue.append(ut)

        if len(update_queue) > 0:
            _LOG.info(f"UPDATING: {len(update_queue)} transactions will be approved")
            tw = UpdateTransactionsWrapper(update_queue)
            if not dry_run:
                await client.patch(UpdateMultipleTransactions(budget_id), tw)


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
    payees_parser.add_argument(
        "-c",
        "--create-payees",
        action="store_true",
        help="If the transactions contain unknown payees, create them in YNAB",
    )
    categories_parser = assign_sub_parsers.add_parser("categories")
    categories_parser.set_defaults(func=assign_categories)
    categories_parser.add_argument(
        "-w",
        "--weekwise",
        action="store_true",
        help="Also iterate over and assign categories for week-wise payees. These will get a different category depending on the transaction date",
    )
    categories_parser.add_argument(
        "-f",
        "--filter",
        type=TransactionType.from_str,
        choices=[None] + [t for t in TransactionType],
        default=TransactionType.UNCATEGORIZED,
        help="Select which set of transactions to update (case-insensitive)",
    )
    categories_parser.add_argument(
        "-F",
        "--force",
        action="store_true",
        help="Force all found transactions to be recategorized",
    )
    matches = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if not DEFAULT_CONFIG_FILE.exists():
        config = Config.create(DEFAULT_CONFIG_FILE)
    else:
        config = Config.load(DEFAULT_CONFIG_FILE)

    if matches.dry_run:
        _LOG.info("Dry-run mode enabled. Not committing any changes")

    await matches.func(matches, config)


if __name__ == "__main__":
    main()
