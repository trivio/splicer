from __future__ import annotations

from functools import partial
from typing import Any, Optional

from zipper import Loc  # type: ignore

from ..relation import Relation
from ..schema import Schema


class Adapter:
    """
    Adapter objects provide relations to the dataset.
    """

    @property
    def relations(self) -> list[tuple[str, Schema]]:
        """
        May return a list of name and schema of -some- of the relations
        the adapter supports.

        Some adapters like HTTP etc.. will create tables on the fly
        based on the passed in URL so introspection is not possible
        """
        return []

    def get_relation(self, name: str) -> Optional[Relation]:
        """Return the relation (table, view, etc..) with the given name or None if this
        adapter does not have the given table."""

    def has(self, relation: str) -> bool:
        """Return true if the Adapter can resolve the relation"""
        ...

    def table_scan(self, name: str, ctx: Any) -> Any:  # TODO.. should this be Table?
        raise NotImplementedError(
            "{} has not implemented table_scan".format(self.__class__.__name__)
        )

    def evaluate(self, loc: Loc) -> Loc:
        op = loc.node()
        func = partial(self.table_scan, op.name)
        # func.schema = op.schema
        return loc.replace(Relation(self, op.name, self.schema(op.name), func))

    def schema(self, name: str) -> Optional[Schema]:
        raise NotImplementedError(
            "{} has not implemented schema".format(self.__class__.__name__)
        )
