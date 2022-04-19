from typing import Any, TypedDict, cast

from . import protocols
from .protocols import FieldType, Mode


class FieldAsDict(TypedDict, total=False):
    name: str
    type: FieldType
    mode: Mode
    fields: list[Any]  # to bad fileds: list[FieldAsDict] causes cyclic errors


class Field(protocols.Field):
    __slots__ = {
        "name": "-> string [REQUIRED]",
        "type": "-> string [REQUIRED] integer|float|string|boolean|date|datetime|time|record",
        "mode": "-> string [OPTIONAL] REQUIRED|NULLABLE|REPEATED: default NULLABLE",
        "fields": "-> list [OPTIONAL IF type = RECORD]",
        "schema_name": "-> string [OPTIONAL]",
    }

    def __init__(
        self,
        name: str,
        type: FieldType,
        mode: Mode = "NULLABLE",
        schema_name: str = None,
        fields: list[protocols.Field | FieldAsDict] = [],
    ):
        self.name = name
        self.type = type
        self.mode = mode
        self.schema_name = schema_name

        self.fields = [
            f if isinstance(f, Field) else Field(**cast(FieldAsDict, f)) for f in fields
        ]

    def __repr__(self) -> str:
        return "<Field(name={name}, type={type} at {id}>".format(
            id=id(self), name=self.name, type=self.type
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            raise NotImplemented

        return (
            self.name == other.name
            and self.type == other.type
            and self.mode == other.mode
            and self.fields == other.fields
            and self.schema_name == other.schema_name
        )

    @property
    def path(self) -> str:
        if self.schema_name:
            return self.schema_name + "." + self.name
        else:
            return self.name

    def new(self, **parts: Any) -> "Field":
        attrs = {attr: getattr(self, attr) for attr in self.__slots__}
        attrs.update(parts)

        return Field(**attrs)

    def to_dict(self) -> FieldAsDict:
        return FieldAsDict(
            # schema_name = self.schema_name,
            name=self.name,
            type=self.type,
            mode=self.mode,
            fields=[cast(dict, f.to_dict()) for f in self.fields],
        )
