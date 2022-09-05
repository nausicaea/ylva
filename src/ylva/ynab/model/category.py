from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options


@dataclass
class Category(DataClassDictMixin):
    id_: str = field(metadata=field_options(alias="id"))
    category_group_id: str
    name: str
    hidden: bool
    original_category_group_id: str
    note: str
    budgeted: int
    activity: int
    balance: int
    goal_type: str
    goal_creation_month: str
    goal_target: int
    goal_target_month: str
    goal_percentage_complete: int
    goal_months_to_budget: int
    goal_under_funded: int
    goal_overall_funded: int
    goal_overall_left: int
    deleted: bool
