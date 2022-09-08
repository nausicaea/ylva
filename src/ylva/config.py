import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from mashumaro.mixins.yaml import DataClassYAMLMixin

from . import YML_SUFFIX, YML_SUFFIXES

_LOG: logging.Logger = logging.getLogger(__name__)


@dataclass
class Config(DataClassYAMLMixin):
    payee_to_category: Dict[str, str] = field(default_factory=dict)
    api_url: str = field(default="https://api.youneedabudget.com/")
    budget_id: str = field(default="default")
    api_token: Optional[str] = field(default=None)
    op_item_id: Optional[str] = field(default=None)
    rate_limit: Optional[float] = field(default=None)

    def save(self, dst: Path) -> None:
        if dst.suffix not in YML_SUFFIXES:
            _LOG.warning(f"Config file suffix does not match the YAML format: {dst}")
            dst = dst.with_suffix(YML_SUFFIX)

        dst.parent.mkdir(parents=True)

        data = self.to_yaml()
        write_mode = "wt" if isinstance(data, str) else "wb"
        with dst.open(write_mode) as f:
            f.write(data)

    @classmethod
    def load(cls, src: Path) -> "Config":
        with src.open("rt") as f:
            return cls.from_yaml(f.read())

    @classmethod
    def create(cls, dst: Path) -> "Config":
        dflt = cls()
        dflt.save(dst)
        return dflt
