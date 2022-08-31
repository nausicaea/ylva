from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class CurrencyFormat(DataClassDictMixin):
    iso_code: str
    example_format: str
    decimal_digits: int
    decimal_separator: str
    symbol_first: bool
    group_separator: str
    currency_symbol: str
    display_symbol: bool
