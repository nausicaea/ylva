from dataclasses import dataclass
from typing import List, Optional

from mashumaro import DataClassDictMixin

from .budgets_entry import BudgetsEntry


@dataclass
class BudgetsList(DataClassDictMixin):
    budgets: List[BudgetsEntry]
    default_budget: Optional[BudgetsEntry]
