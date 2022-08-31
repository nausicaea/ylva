from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from mashumaro import DataClassDictMixin, field_options

from .account import Account
from .currency_format import CurrencyFormat
from .date_format import DateFormat


@dataclass
class Budget(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    name: str
    last_modified_on: datetime
    first_month: date
    last_month: date
    date_format: DateFormat
    currency_format: CurrencyFormat
    accounts: Optional[List[Account]] = field(default=None)
