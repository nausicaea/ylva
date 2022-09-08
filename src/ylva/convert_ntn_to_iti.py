from typing import Dict

from ingridr import Iter
from reidun.client import ApiClient

from .list_categories import list_categories
from .list_payees import list_payees


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
    :raise ValueError: when there are no payees or categories
    """
    payees = await list_payees(client, budget_id)
    categories = await list_categories(client, budget_id)

    iti: Dict[str, str] = dict()
    for pn, cn in ntn.items():
        pi = Iter(payees).filter(lambda e: e.name == pn).map(lambda e: e.id_).next()

        ci = Iter(categories).filter(lambda e: e.name == cn).map(lambda e: e.id_).next()
        if pi is not None and ci is not None:
            iti[pi] = ci

    return iti
