from typing import Dict, Iterable, Protocol, runtime_checkable

from ingridr import Iter

from .ynab.model.category import Category
from .ynab.model.payee import Payee


@runtime_checkable
class NamedId(Protocol):
    def name(self) -> str:
        ...

    def id(self) -> str:
        ...


def convert_names_to_ids(names: Iterable[str], lut: Iterable[NamedId]) -> list[str]:
    ids: list[str] = list()
    for n in names:
        i = Iter(lut).filter(lambda e: e.name() == n).map(lambda e: e.id()).next()
        if i is not None:
            ids.append(i)

    return ids


def convert_ntn_to_iti(
    ntn: Dict[str, str], payees: Iterable[Payee], categories: Iterable[Category]
) -> Dict[str, str]:
    """
    Convert a mapping of payee names to category names into a mapping of
    payee IDs to category IDs

    :param ntn: the name-to-name mapping of payees and categories
    :param payees: an iterable of payees
    :param categories: an iterable of categories
    :returns: the id-to-id mapping of payees and categories
    :raise ValueError: when there are no payees or categories
    """
    iti: Dict[str, str] = dict()
    for pn, cn in ntn.items():
        pi = Iter(payees).filter(lambda e: e.name == pn).map(lambda e: e.id_).next()

        ci = Iter(categories).filter(lambda e: e.name == cn).map(lambda e: e.id_).next()
        if pi is not None and ci is not None:
            iti[pi] = ci

    return iti
