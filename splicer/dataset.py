from typing import Any, Callable, Optional

from zipper import Loc  # type: ignore

from . import compat, functions, protocols
from .adapters.null_adapter import NullAdapter
from .aggregate import Aggregate  # type: ignore
from .ast import AliasOp, Expr, LoadOp, RelationalOp
from .compilers import local  # type: ignore
from .compilers.local import relational_function  # type: ignore
from .field import Field
from .operations import walk  # type: ignore
from .protocols import Adapter
from .query import Query, view_replacer
from .query_builder import QueryBuilder  # type: ignore
from .query_parser import parse_statement  # type: ignore

DumpFunc = Callable[[protocols.Schema, protocols.Relation], None]


class DataSet(object):
    def __init__(self) -> None:
        self.adapters: list[Adapter] = [NullAdapter()]

        self.relation_cache: dict[str, protocols.Relation] = {}

        self.views: dict[str, AliasOp] = {}
        # self.schema_cache = {}
        self.executor = None
        self.compile: Callable[..., Any] = local.compile  # type: ignore
        self.dump_func: Optional[DumpFunc] = None
        self.udfs: dict[str, Callable[..., Any]] = {}

        self.aggregates: dict[str, Aggregate] = {}

        functions.init(self)  # type: ignore

    def add_adapter(self, adapter: Adapter) -> Adapter:
        """
        Add the given adapter to the dataset.

        Multiple adds for the instance of the same
        adapter are ignored.

        """

        if adapter not in self.adapters:
            self.adapters.append(adapter)
        return adapter

    def create_view(self, name: str, query_or_operations: str | RelationalOp) -> None:
        if isinstance(query_or_operations, str):
            operations = self.query(query_or_operations).operations
        else:
            operations = query_or_operations

        self.views[name] = AliasOp(name, operations, operations.schema)

    def aggregate(self, returns=None, initial=None, name=None, finalize=None):  # type: ignore
        def _(func, name):  # type: ignore
            if name is None:
                name = func.__name__
            self.add_aggregate(name, func, returns, initial, finalize)
            return func

        return _

    def function(self, returns=None, name=None):  # type: ignore
        """Decorator for registering functions

        @dataset.function
        def somefunction():
          pass


        """

        def _(func, name=name):  # type: ignore
            if name is None:
                name = func.__name__
            self.add_function(name, func, returns)
            return func

        return _

    def add_aggregate(self, name, func, returns, initial, finalize=None):  # type: ignore
        self.aggregates[name] = Aggregate(
            function=func, returns=returns, initial=initial, finalize=finalize
        )

    def add_function(self, name, function, returns=None):  # type: ignore
        if name in self.udfs:
            raise ValueError("Function {} already registered".format(name))

        if returns:
            if callable(returns):
                function.returns = returns
            else:
                function.returns = Field(**returns)
        else:
            function.returns = None

        self.udfs[name] = function

    def get_function(self, name: str) -> Callable[..., Any]:
        function = self.udfs.get(name) or self.aggregates.get(name)
        if function:
            return function
        else:
            raise NameError("No function named {}".format(name))

    def get_view(self, name: str) -> Optional[AliasOp]:
        return self.views.get(name)

        view = self.views.get(name)
        if view:
            return replace_views(view, self)
        else:
            return None

    @property
    def relations(self) -> list[tuple[str, protocols.Relation]]:
        """
        Returns a list of all relations from all adapters
        note this could be a slow operation as remote
        calls must be made to each adapter.

        As a side effect the relation_cache will be updated.
        """

        for adapter in self.adapters:
            for name, schema in adapter.relations:
                self.relation_cache[name] = schema
        return [item for item in self.relation_cache.items() if item[0] != ""]

    def adapter_for(self, relation: str) -> Optional[Adapter]:
        for adapter in self.adapters:
            if adapter.has(relation):
                return adapter
        return None

    def get_relation(self, name: str) -> Optional[protocols.Relation]:
        """Returns the relation for the given name.

        The dataset will search all adapters in the order the
        adapters were added to the dataset returning the first
        relation with the given name.
        """
        relation = self.relation_cache.get(name)
        if relation is None:
            for adapter in self.adapters:
                relation = adapter.get_relation(name)
                if relation:
                    self.relation_cache[name] = relation
                    break

        return relation

    def get_schema(self, name: str) -> protocols.Schema:
        """
        Returns the schema for relation found with the given name.

        The search order is the same as dataset.get_relation()
        """

        return Query(self, LoadOp(name)).schema

        # schema_or_expr = self.adapter_for(name).schema(name)
        # if not isinstance(schema_or_expr, Expr):
        #   return schema_or_expr
        # else:
        #   # it's an expression compile it... seems weird
        #   # that the compile function is 'relational_function'
        #   func = relational_function(self, schema_or_expr)
        #   return func({})

    def set_compiler(self, compile_fun: Callable[..., Any]) -> None:
        self.compile = compile_fun

    def set_dump_func(self, dump_func: DumpFunc) -> None:
        self.dump_func = dump_func

    def dump(self, schema: protocols.Schema, relation: protocols.Relation) -> None:
        if self.dump_func is not None:
            self.dump_func(schema, relation)

    def execute(self, query: Query | str, *params: Any) -> Any:
        if isinstance(query, str):
            query = self.query(query)

        func = self.compile(query)
        ctx = {"dataset": self, "params": params}

        return func(ctx)

    def query(self, statement: str) -> Query:
        """Parses the statement and returns a Query"""
        return Query(self, parse_statement(statement))

    def frm(self, relation_or_stmt):  # type: ignore
        return QueryBuilder(self).frm(relation_or_stmt)

    def select(self, *cols):  # type: ignore
        return QueryBuilder(self).select(*cols)


def replace_views(operation: RelationalOp, dataset: DataSet) -> RelationalOp:
    def adapt(loc: Loc) -> Loc:
        node = loc.node()
        if isinstance(node, LoadOp):
            return view_replacer(dataset, loc, node)
        else:
            return loc

    return walk(operation, adapt)
