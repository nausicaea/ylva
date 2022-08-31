from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from mashumaro import DataClassDictMixin, field_options

from .budget_accounts_entry import BudgetAccountsEntry
from .currency_format import CurrencyFormat
from .date_format import DateFormat


@dataclass
class BudgetsEntry(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    name: str
    last_modified_on: datetime
    first_month: date
    last_month: date
    date_format: DateFormat
    currency_format: CurrencyFormat
    accounts: Optional[List[BudgetAccountsEntry]] = field(default=None)
