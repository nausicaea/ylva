import logging
from argparse import ArgumentParser, Namespace
from typing import List, cast

from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from ylva.ynab.model.save_transaction import SaveTransaction
from ylva.ynab.model.transaction_status import TransactionStatus
from ylva.ynab.transactions.update import (SaveTransactionWrapper,
                                           UpdateTransaction)

from ..ynab.payees.list import ListPayees, PayeesResponse
from ..ynab.transactions.list import (ListTransactions, TransactionsResponse,
                                      TransactionType)
from . import start

_LOG: logging.Logger = logging.getLogger(__name__)


async def assign_payees(matches: Namespace) -> None:
    dry_run: bool = matches.dry_run
    api_url: str = matches.api_url
    api_token: str = matches.api_token
    budget_id: str = matches.budget

    async with ApiClient(api_url, auth=BearerAuth(api_token)) as client:
        payees, _ = await client.get(ListPayees(budget_id))
        if payees is None:
            return

        lt = ListTransactions(budget_id)
        ltp = lt.params().with_type(TransactionType.UNCATEGORIZED).build()
        transactions, _ = await client.get(lt, params=ltp)
        if transactions is None:
            return

        update_queue: List[SaveTransaction] = list()
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
            elif t.payee_id is not None:
                _LOG.debug(
                    f"SKIPPING: Transaction {t.id_}  ({t.date} - {t.amount}) has an assigned payee"
                )
                continue
            elif t.memo is None:
                _LOG.warning(
                    f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has no memo, so I cannot find the appropriate payee"
                )
                continue
            elif len(t.memo) > 200:
                _LOG.warning(
                    f"SKIPPING: Transaction {t.id_} ({t.date} - {t.amount}) has a memo over 200 characters. YNAB will complain when updating this transaction"
                )
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


async def assign_categories(matches: Namespace) -> None:
    raise NotImplementedError()


@start
async def main() -> None:
    parser = ArgumentParser(prog="ylva")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
    )
    sub_parsers = parser.add_subparsers(required=True, dest="root")
    assign_parser = sub_parsers.add_parser("assign")
    assign_parser.add_argument(
        "-b",
        "--budget",
        default="default",
    )
    assign_parser.add_argument(
        "-a",
        "--api-url",
        default="https://api.youneedabudget.com/",
    )
    assign_parser.add_argument(
        "-t",
        "--api-token",
    )
    assign_sub_parsers = assign_parser.add_subparsers(required=True, dest="assign")
    payees_parser = assign_sub_parsers.add_parser("payees")
    payees_parser.set_defaults(func=assign_payees)
    categories_parser = assign_sub_parsers.add_parser("categories")
    categories_parser.set_defaults(func=assign_categories)
    matches = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    await matches.func(matches)


if __name__ == "__main__":
    main()
