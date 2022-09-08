from dataclasses import dataclass

from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass
class Cache(DataClassYAMLMixin):
    pass
