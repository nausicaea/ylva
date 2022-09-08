import logging
from typing import Dict, cast

from ingridr import Iter
from reidun.client import ApiClient

from .ynab.categories.list import CategoriesResponse, ListCategories
from .ynab.payees.list import ListPayees, PayeesResponse

_LOG: logging.Logger = logging.getLogger(f"{__package__}.ylva")


async def convert_ntn_to_iti(
    client: ApiClient, budget_id: str, ntn: Dict[str, str]
) -> Dict[str, str]:
    """
    Convert a mapping of payee names to category names into a mapping of
    payee IDs to category IDs

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve transactions from
    :param ntn: the name-to-name mapping of payees and categories
    :returns: the id-to-id mapping of payees and categories
    """
    payees, _ = await client.get(ListPayees(budget_id))
    if payees is None:
        _LOG.warning(f"Budget {budget_id} has no payees")
        return dict()
    payees = cast(PayeesResponse, payees)

    categories, _ = await client.get(ListCategories(budget_id))
    if categories is None:
        _LOG.warning(f"Budget {budget_id} has no categories")
        return dict()
    categories = cast(CategoriesResponse, categories)

    iti: Dict[str, str] = dict()
    for pn, cn in ntn.items():
        pi = (
            Iter(payees.data.payees)
            .filter(lambda e: e.name == pn)
            .map(lambda e: e.id_)
            .next()
        )

        ci = (
            Iter(categories.data.category_groups)
            .map(lambda e: e.categories)
            .flatten()
            .filter(lambda e: e.name == cn)
            .map(lambda e: e.id_)
            .next()
        )
        if pi is not None and ci is not None:
            iti[pi] = ci

    return iti
