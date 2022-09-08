from dataclasses import dataclass, field
from typing import List

from mashumaro import DataClassDictMixin, field_options

from . import Id
from .category import Category


@dataclass
class CategoryGroup(DataClassDictMixin):
    id_: Id = field(metadata=field_options(alias="id"))
    name: str
    hidden: bool
    deleted: bool
    categories: List[Category]
