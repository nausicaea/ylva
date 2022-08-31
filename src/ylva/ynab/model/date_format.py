from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options


@dataclass
class DateFormat(DataClassDictMixin):
    format_: str = field(metadata=field_options(alias="format"))
