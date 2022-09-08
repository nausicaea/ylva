from typing import Iterable, Mapping, TypeVar

from .ynab.model import Id
from .ynab.model.category import Category
from .ynab.model.payee import Payee

A1 = TypeVar("A1")
B1 = TypeVar("B1")
A2 = TypeVar("A2")
B2 = TypeVar("B2")


def create_nti_lut(data: Iterable[Payee] | Iterable[Category]) -> dict[str, Id]:
    """
    Build a lookup table (a reference mapping) of names to IDs

    :param data: an iterable of payees or categories
    :returns: a mapping of names to IDs
    """
    return {e.name: e.id_ for e in data}


def create_itn_lut(data: Iterable[Payee] | Iterable[Category]) -> dict[Id, str]:
    """
    Build a lookup table (a reference mapping) of IDs to names

    :param data: an iterable of payees or categories
    :returns: a mapping of IDs to names
    """
    return {e.id_: e.name for e in data}


def convert_a_to_b(idents_a: Iterable[A1], lut: Mapping[A1, B1]) -> list[B1]:
    """
    Convert an iterable of identifiers A into an iterable of identifiers B. If
    you have two unique identifiers for a particular object, you can use this
    function to convert a sequence of type A identifiers into a sequence of
    type B identifiers.

    :param idents_a: the iterable of names
    :param lut: a reference mapping of identifier A to identifier B
    :returns: a list of identifiers B
    """
    return [lut[a] for a in idents_a if a in lut]


def convert_ata_to_btb(
    ata: Mapping[A1, A2], key_lut: Mapping[A1, B1], value_lut: Mapping[A2, B2]
) -> dict[B1, B2]:
    """
    Convert a mapping of identifiers A-to-A to a mapping of identifiers B-to-B.
    If you have two unique identifiers for a particular object, you can use
    this function to convert a relationship of two objects established by the
    first identifier into a relationship of the same objects using the second
    identifier.

    :param ata: the A-to-A mapping (ex. payee to category names)
    :param key_lut: a reference mapping of identifiers A to identifiers B for the input mapping keys (ex. payee names to IDs)
    :param value_lut: a reference mapping of identifiers A to identifiers B for the input mapping values (ex. category names to IDs)
    """
    return {
        key_lut[ak]: value_lut[av]
        for ak, av in ata.items()
        if ak in key_lut and av in value_lut
    }


def convert_ata_to_atb(
    ata: Mapping[A1, A2], value_lut: Mapping[A2, B2]
) -> dict[A1, B2]:
    """
    Convert a mapping of identifiers A-to-A to a mapping of identifiers A-to-B.

    :param ata: the A-to-A mapping (ex. payee to category names)
    :param value_lut: a reference mapping of identifiers A to identifiers B for the input mapping values (ex. category names to IDs)
    """
    return {ak: value_lut[av] for ak, av in ata.items() if av in value_lut}
