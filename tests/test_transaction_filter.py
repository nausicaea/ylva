import datetime
import itertools
from typing import Optional

import pytest

from ylva.transaction_filter import TFilter, predicate_transaction
from ylva.ynab.model import Id
from ylva.ynab.model.transaction import Transaction
from ylva.ynab.model.transaction_status import TransactionStatus


def _trn(
    c: TransactionStatus = TransactionStatus.UNCLEARED,
    m: Optional[str] = None,
    pi: Optional[Id] = None,
    pn: Optional[str] = None,
    ci: Optional[Id] = None,
    cn: Optional[str] = None,
    tai: Optional[Id] = None,
    tti: Optional[Id] = None,
    mti: Optional[Id] = None,
    ii: Optional[Id] = None,
) -> Transaction:
    return Transaction(
        id_=Id("id_"),
        date=datetime.date.today(),
        amount=0,
        memo=m,
        cleared=c,
        approved=False,
        flag_color="flag_color",
        account_id=Id("account_id"),
        account_name="account_name",
        payee_id=pi,
        payee_name=pn,
        category_id=ci,
        category_name=cn,
        transfer_account_id=tai,
        transfer_transaction_id=tti,
        matched_transaction_id=mti,
        import_id=ii,
        deleted=False,
        subtransactions=list(),
    )


@pytest.mark.parametrize(
    "t,f,exp",
    [
        (_trn(tti=Id("tti")), TFilter.TRANSFER, True),
        (_trn(tti=None), TFilter.TRANSFER, False),
        (_trn(tti=Id("tti")), TFilter.NO_TRANSFER, False),
        (_trn(tti=None), TFilter.NO_TRANSFER, True),
        (_trn(c=TransactionStatus.RECONCILED), TFilter.RECONCILED, True),
        (_trn(c=TransactionStatus.UNCLEARED), TFilter.RECONCILED, False),
        (_trn(c=TransactionStatus.CLEARED), TFilter.RECONCILED, False),
        (_trn(c=TransactionStatus.RECONCILED), TFilter.NOT_RECONCILED, False),
        (_trn(c=TransactionStatus.UNCLEARED), TFilter.NOT_RECONCILED, True),
        (_trn(c=TransactionStatus.CLEARED), TFilter.NOT_RECONCILED, True),
        (_trn(c=TransactionStatus.RECONCILED), TFilter.CLEARED, False),
        (_trn(c=TransactionStatus.UNCLEARED), TFilter.CLEARED, False),
        (_trn(c=TransactionStatus.CLEARED), TFilter.CLEARED, True),
        (_trn(c=TransactionStatus.RECONCILED), TFilter.NOT_CLEARED, True),
        (_trn(c=TransactionStatus.UNCLEARED), TFilter.NOT_CLEARED, True),
        (_trn(c=TransactionStatus.CLEARED), TFilter.NOT_CLEARED, False),
        (_trn(pi=Id("payee_id")), TFilter.ASSIGNED_PAYEE, True),
        (_trn(pi=None), TFilter.ASSIGNED_PAYEE, False),
        (_trn(pi=Id("payee_id")), TFilter.NO_PAYEE, False),
        (_trn(pi=None), TFilter.NO_PAYEE, True),
        (_trn(ci=Id("category_id")), TFilter.ASSIGNED_CATEGORY, True),
        (_trn(ci=None), TFilter.ASSIGNED_CATEGORY, False),
        (_trn(ci=Id("category_id")), TFilter.NO_CATEGORY, False),
        (_trn(ci=None), TFilter.NO_CATEGORY, True),
        (_trn(m="memo"), TFilter.ASSIGNED_MEMO, True),
        (_trn(m="".join(itertools.repeat("m", 201))), TFilter.ASSIGNED_MEMO, True),
        (_trn(m=None), TFilter.ASSIGNED_MEMO, False),
        (_trn(m="memo"), TFilter.NO_MEMO, False),
        (_trn(m="".join(itertools.repeat("m", 201))), TFilter.NO_MEMO, False),
        (_trn(m=None), TFilter.NO_MEMO, True),
    ],
)
def test_predicate_transaction(t: Transaction, f: TFilter, exp: bool) -> None:
    assert predicate_transaction(t, f) == exp
