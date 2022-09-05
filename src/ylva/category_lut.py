from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CategoryLut:
    payee_id_to_category_id: Dict[str, str] = field(default_factory=dict)
    payee_name_to_category_name: Dict[str, str] = field(default_factory=dict)
    monthweek_to_category_id: Dict[int, str] = field(default_factory=dict)
