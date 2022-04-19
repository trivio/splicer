from typing import Any, Callable, Collection, Optional, cast

from . import protocols
from .immutable import ImmutableMixin

# from .schema import Schema
from .protocols import Schema
from .table import Table  # type: ignore


class Expr(ImmutableMixin):
    def __eq__(self, other: Any) -> bool:

        result = isinstance(other, self.__class__) and all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__slots__
            if attr != "schema"
        )

        return result

    def __ne__(self, other: Any) -> bool:
        return not self == other


class UnaryOp(Expr):
    __slots__ = ("expr",)

    def __init__(self, expr: Expr):
        self.expr = expr


class NegOp(UnaryOp):
    """- (expr)"""

    __slots__ = ("expr",)


class NotOp(UnaryOp):
    """not (expr)"""

    __slots__ = ("expr",)


class ItemGetterOp(Expr):
    """(expr)[key]"""

    __slots__ = ("key",)

    def __init__(self, key: str):
        self.key = key


class BinaryOp(Expr):
    __slots__ = ("lhs", "rhs")

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs
        self.rhs = rhs


class And(BinaryOp):
    """lhs and rhs"""

    __slots__ = ("lhs", "rhs")


class Or(BinaryOp):
    """lhs or rhs"""

    __slots__ = ("lhs", "rhs")


class LtOp(BinaryOp):
    """Less than"""

    __slots__ = ("lhs", "rhs")


class LeOp(BinaryOp):
    """Less than or equal to"""

    __slots__ = ("lhs", "rhs")


class EqOp(BinaryOp):
    """Equal to"""

    __slots__ = ("lhs", "rhs")


class NeOp(BinaryOp):
    """Not equal to"""

    __slots__ = ("lhs", "rhs")


class GeOp(BinaryOp):
    """Greater than or equal to"""

    __slots__ = ("lhs", "rhs")


class GtOp(BinaryOp):
    """Greater than"""

    __slots__ = ("lhs", "rhs")


class IsOp(BinaryOp):
    """x is y"""

    __slots__ = ("lhs", "rhs")


class IsNotOp(BinaryOp):
    """x is not y"""

    __slots__ = ("lhs", "rhs")


class LikeOp(BinaryOp):
    """x LIKE y"""

    __slots__ = ("lhs", "rhs")


class NotLikeOp(BinaryOp):
    """x LIKE y"""

    __slots__ = ("lhs", "rhs")


class NotRLikeOp(BinaryOp):
    """x Not RLIKE y"""

    __slots__ = ("lhs", "rhs")


class RLikeOp(BinaryOp):
    """x RLIKE y"""

    __slots__ = ("lhs", "rhs")


class RegExpOp(BinaryOp):
    """x RLIKE y"""

    __slots__ = ("lhs", "rhs")


class InOp(BinaryOp):
    """x is y"""

    __slots__ = ("lhs", "rhs")


class AddOp(BinaryOp):
    """lhs + rhs"""

    __slots__ = ("lhs", "rhs")


class SubOp(BinaryOp):
    """lhs - rhs"""

    __slots__ = ("lhs", "rhs")


class MulOp(BinaryOp):
    """lhs * rhs"""

    __slots__ = ("lhs", "rhs")


class DivOp(BinaryOp):
    """lhs / rhs"""

    __slots__ = ("lhs", "rhs")


class BetweenOp(BinaryOp):
    """x between lhs and rhs"""

    __slots__ = ("expr", "lhs", "rhs")

    def __init__(self, expr: Expr, lhs: Expr, rhs: Expr):
        self.expr = expr
        self.lhs = lhs
        self.rhs = rhs


# Postgres Specific operators
class JsonOp(BinaryOp):
    """columns -> 'some path'"""

    __slots__ = ("lhs", "rhs")


# Postgres Specific operators
class JsonTextOp(BinaryOp):
    """columns -> 'some path'"""

    __slots__ = ("lhs", "rhs")


class Const(Expr):
    __slots__ = ("const",)

    def __init__(self, const: str | bool | int | float | None):
        self.const = const


class NullConst(Const):
    """Null or None"""

    __slots__ = ()
    const: None = None

    def __init__(self) -> None:
        pass


class NumberConst(Const):
    """Integer or Float"""

    __slots__ = ("const",)


class StringConst(Const):
    """A string"""

    __slots__ = ("const",)


class BoolConst(Const):
    """A boolean const"""

    __slots__ = ()

    def __init__(self) -> None:
        pass


class TrueConst(BoolConst):
    """The constant True"""

    __slots__ = ()
    const: bool = True


class FalseConst(BoolConst):
    """The constant False"""

    __slots__ = ()
    const: bool = False


class Var(Expr):
    __slots__ = ("path",)

    def __init__(self, path: str):
        self.path = path


class Tuple(Expr):
    __slots__ = ("exprs",)

    def __init__(self, *exprs: Expr):
        self.exprs = exprs


class Function(Expr):
    __slots__ = ("name", "args", "schema", "func")

    def __init__(self, name: str, *args: Any, **kw: Any):
        self.name = name
        self.args = args
        self.schema = kw.get("schema")
        self.func: Callable[..., Any] = cast(Callable[..., Any], kw.get("func"))

    def __call__(self, ctx: Any) -> Any:
        return self.func(ctx)


COMPARISON_OPS: dict[str, type] = {
    "<": LtOp,
    "<=": LeOp,
    "=": EqOp,
    "!=": NeOp,
    ">=": GeOp,
    ">": GtOp,
    "is": IsOp,
    "is not": IsNotOp,
    "like": LikeOp,
    "rlike": RLikeOp,
    "not like": NotLikeOp,
    "not rlike": NotRLikeOp,
    "regexp": RegExpOp,
    # Postgres opperators
    "->": JsonOp,
    "->>": JsonTextOp,
}


MULTIPLICATIVE_OPS: dict[str, type] = {"*": MulOp, "/": DivOp}

ADDITIVE_OPS: dict[str, type] = {"+": AddOp, "-": SubOp}

# sql specific expresions


class Asc(UnaryOp):
    """Sort from lowest to highest"""

    __slots__ = ("expr",)


class Desc(UnaryOp):
    """Sort from highest to lowest"""

    __slots__ = ("expr",)


class ParamGetterOp(UnaryOp):
    """?<number>"""

    __slots__ = ("expr",)


class SelectAllExpr(Expr):
    __slots__ = ("table",)

    def __init__(self, table: Table = None):
        self.table = table


class RenameOp(Expr):
    __slots__ = ("name", "expr")

    def __init__(self, name: str, expr: Expr):
        self.name = name
        self.expr = expr


class RelationalOp(Expr):
    schema: Optional[Schema] = None


class LoadOp(RelationalOp):
    """Load a relation with the given name"""

    __slots__ = ("name", "schema")

    def __init__(self, name: str, schema: Schema = None):
        self.name = name
        self.schema = schema


class AliasOp(RelationalOp):
    """Rename the relation to the given name"""

    __slots__ = ("relation", "name", "schema")

    def __init__(self, name: str, relation: RelationalOp, schema: Schema = None):
        self.name = name
        self.relation = relation
        self.schema = schema


class ProjectionOp(RelationalOp):
    __slots__ = ("relation", "exprs", "schema")

    def __init__(
        self, relation: RelationalOp, *exprs: Expr, schema: Schema = None, **kw: Any
    ):
        self.relation = relation
        self.exprs = exprs
        self.schema = schema


class DistinctOp(RelationalOp):
    __slots__ = ("relation",)

    def __init__(self, relation: RelationalOp):
        self.relation = relation


class SelectionOp(RelationalOp):
    __slots__ = ("relation", "bool_op", "schema")

    def __init__(self, relation: RelationalOp, bool_op: Expr, schema: Schema = None):
        self.relation = relation
        self.bool_op = bool_op
        self.schema = schema


class CaseWhenOp(RelationalOp):
    __slots__ = ("conditions", "default_value")

    def __init__(self, conditions: Collection[Expr], default_value: Any):
        self.conditions = conditions
        self.default_value = default_value


class CastOp(RelationalOp):
    __slots__ = ("expr", "type")

    def __init__(self, expr: Expr, type: type):
        self.expr = expr
        self.type = type


class BinRelationalOp(RelationalOp):
    """
    RelationalOp that operates on two relations
    """

    __slots__ = ("left", "right", "schema")


class UnionAllOp(BinRelationalOp):
    """Combine the results of multiple operations with identical schemas
    into one.
    """

    __slots__ = ("left", "right", "schema")

    def __init__(self, left: RelationalOp, right: RelationalOp, schema: Schema = None):
        self.left = left
        self.right = right
        self.schema = schema


class JoinOp(BinRelationalOp):
    __slots__ = ("left", "right", "bool_op", "schema")

    def __init__(
        self,
        left: RelationalOp,
        right: RelationalOp,
        bool_op: BoolConst = TrueConst(),
        schema: Schema = None,
    ):
        self.left = left
        self.right = right
        self.bool_op = bool_op
        self.schema = schema


class LeftJoinOp(JoinOp):
    __slots__ = ("left", "right", "bool_op", "schema")


class OrderByOp(RelationalOp):
    __slots__ = ("relation", "exprs", "schema")

    def __init__(
        self,
        relation: RelationalOp,
        first: Expr,
        schema: Schema = None,
        *exprs: Expr,
        **kw: Any
    ):
        self.relation = relation
        self.exprs = (first,) + exprs
        self.schema = schema

    def new(self, **parts: Any) -> "OrderByOp":
        # OrderByOp's __init__ doesn't match what's defined in __slots__
        # so we have to help it make a copy of this object
        exprs: tuple[Expr] = parts.pop("exprs", self.exprs)
        first = exprs[0]
        tail = exprs[1:]
        relation = parts.pop("relation", self.relation)

        return self.__class__(relation, first, *tail, **parts)


class GroupByOp(RelationalOp):
    __slots__ = ("relation", "aggregates", "exprs", "schema")

    def __init__(
        self, relation: RelationalOp, schema: Schema = None, *exprs: Expr, **kw: Any
    ):
        self.relation = relation
        self.exprs = exprs

        # bit of a kludge, aggregates can't be resolved at
        # parse time, so they start as an empty list and
        # are set when the expression tree is evaluated.
        # See compilers.local.projection_op for details
        self.aggregates: tuple[Any, ...] = kw.get("aggregates", ())

        self.schema = schema


class SliceOp(RelationalOp):
    __slots__ = ("relation", "start", "stop", "schema")

    def __init__(
        self, relation: RelationalOp, schema: Schema = None, *args: int, **kw: Any
    ):
        self.relation = relation
        if len(args) == 1:
            self.start = 0
            self.stop = args[0]
        else:
            self.start, self.stop = args

        self.schema = schema

    def new(self, **parts: Any) -> "SliceOp":
        # slice op's __init__ doesn't match what's defined in __slots__
        # so we have to help it make a copy of this object
        args = parts.pop("start", self.start), parts.pop("stop", self.stop)
        relation = parts.pop("relation", self.relation)

        return self.__class__(relation, *args, **parts)
