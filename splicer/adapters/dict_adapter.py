from typing import Any, Iterator, Optional, Sequence, TypedDict, cast

from splicer import Table

from ..protocols import Relation
from ..schema import Schema, SchemaAsDict
from . import Adapter


class DictTableAsDict(TypedDict):
    schema: SchemaAsDict
    rows: Sequence[Any]


class DictAdapter(Adapter):
    """
    An adapter for working with lists of dictionaries.
    """

    def __init__(self, **tables: DictTableAsDict):
        """

        Examples:
        Dictionary(
          users=[dict(),dict(),...],
          other=dict(
            schema=[],
            rows=[dict(),dict(),...]
          )
        )

        """
        self._tables: dict[str, DictTable] = {}

        for name, table in tables.items():

            schema = Schema(**table["schema"])
            rows = table["rows"]

            self._tables[name] = DictTable(self, name, schema=schema, rows=rows)

    @property
    def relations(self) -> list[tuple[str, Relation]]:
        return [(name, table) for name, table in self._tables.items()]

    def has(self, relation: str) -> bool:
        return relation in self._tables

    def schema(self, relation: str) -> Schema:
        return self._tables[relation].schema

    def get_relation(self, name: str) -> Optional[Relation]:
        return cast(Optional[Relation], self._tables.get(name))

    def table_scan(self, name: str, ctx: Any) -> Table:
        return self._tables[name]


class DictTable(Table):
    # schema:Schema
    def __init__(
        self, adapter: Adapter, name: str, schema: Schema, rows: Sequence[Any]
    ):
        super(DictTable, self).__init__(adapter, name, schema)  # type: ignore
        self.key_index = [
            (f.name, () if f.mode == "REPEATED" else None) for f in self.schema.fields
        ]
        self._rows = rows

    def __iter__(self) -> Iterator:
        key_index = self.key_index

        return (
            tuple(row.get(key, default) for key, default in key_index)
            for row in self._rows
        )
