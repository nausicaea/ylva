from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

from . import Id


@dataclass
class Category(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    category_group_id: Id
    name: str
    hidden: bool
    original_category_group_id: Id
    note: str
    budgeted: int
    activity: int
    balance: int
    goal_type: str
    goal_creation_month: str
    goal_target: int
    goal_target_month: str
    goal_percentage_complete: int | None
    goal_months_to_budget: int | None
    goal_under_funded: int | None
    goal_overall_funded: int | None
    goal_overall_left: int | None
    deleted: bool
