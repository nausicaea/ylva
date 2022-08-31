from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin

from .. import ResponseWrapper
from .budgets_list import BudgetsList


@dataclass
class Budgets(ResponseWrapper[BudgetsList], DataClassJSONMixin):
    pass
