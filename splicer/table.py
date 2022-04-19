from typing import Any, Iterator, TypeVar

from . import protocols
from .protocols import Adapter
from .schema import Field, Schema

T = TypeVar("T")


class Table(protocols.Relation):
    schema: Schema

    def __init__(self, adapter: Adapter, name: str, schema: protocols.Schema | dict):
        """

        Initialize a table with a name or a schema.

        Args:
          name (str):  The name of the table.
          schema (Schema | dict): Schema for the table specified as a dict
          or instance of the Schema class.

        """

        self.adapter = adapter
        self.name = name

        if isinstance(schema, dict):
            args = schema.copy()
            if "name" not in args:
                args["name"] = name
            self.schema = Schema(**args)
        elif isinstance(schema, Schema):
            self.schema = schema

    @property
    def fields(self) -> list[Field]:
        return self.schema.fields

    def __iter__(self) -> Iterator[T]:
        """
        Returns an iterator of tuples.

        Table implementations from remote adapters should use qualifiers
        and columns to reduce the set of results if they can. This will
        save network bandwidth or disk load time. Splicer will filter and
        take the columns it needs from the rows returned by this method
        regardless so adapters without filtering capabilities are free
        to return the data as is.
        """
        # return iter([])

    def records(self, ctx: Any) -> Any:
        return iter(self)
