from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from splicer.ast import LoadOp

#from .protocols import Adapter, Schema
from .schema import Schema
from .adapters import Adapter

@dataclass
class Relation:
    """
    Represents a list of tuples
    """

    adapter: Adapter
    name: str
    schema: Optional[Schema]
    records: Callable[..., Any]
    # namedtuple('Relation', 'adapter, name, schema, records')

    # __slots__ = ()

    # equality testing mostly used during unit tests
    def __eq__(self, other: object) -> bool:

        if isinstance(other, Relation):
            return self.adapter == other.adapter and self.name == other.name
        elif isinstance(other, LoadOp):
            return self.name == other.name
        else:
            raise NotImplemented

    def __call__(self, ctx: Any) -> Any:
        return self.records(ctx)
