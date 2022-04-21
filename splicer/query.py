from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Iterator, TypeVar

from .ast import AliasOp, LoadOp, RelationalOp
from .operations import isa  # type: ignore
from .protocols import Relation, Schema
from .schema_interpreter import resolve_schema  # type: ignore

if TYPE_CHECKING:
    from zipper import Loc  # type: ignore

    from .dataset import DataSet


T = TypeVar("T")


@dataclass
class Query(Generic[T]):
    dataset: DataSet
    operations: RelationalOp
    schema: Schema

    __slots__ = {"dataset": "-> DataSet", "operations": "ast.Expr", "schema": "Schema"}

    def __init__(self, dataset: DataSet, operations: RelationalOp):
        self.dataset = dataset

        self.operations = resolve_schema(
            dataset, operations, (isa(LoadOp), view_replacer)
        )
        assert self.operations.schema is not None
        self.schema = self.operations.schema

    def __iter__(self) -> Iterator[T]:
        return iter(self.execute())

    def dump(self) -> None:
        self.dataset.dump(self.schema, self.execute())

    def create_view(self, name: str) -> None:
        self.dataset.create_view(name, self.operations)

    def execute(self, *params: Any) -> Any:
        return self.dataset.execute(self, *params)


def view_replacer(dataset: DataSet, loc: Loc, op: AliasOp | LoadOp) -> Loc:
    view = dataset.get_view(op.name)

    if view:
        new_loc = loc.replace(view).leftmost_descendant()
        # keep going until the leftmost_descendant isn't a view
        return view_replacer(dataset, new_loc, new_loc.node())
    else:
        return load_relation(dataset, loc, op)


def load_relation(dataset: DataSet, loc: Loc, op: AliasOp | LoadOp) -> Loc:
    adapter = dataset.adapter_for(op.name)
    if adapter is None:
        raise LookupError(f"No adapter for relation {op.name}")

    return adapter.evaluate(loc)
