from .immutable import ImmutableMixin

class Expr(ImmutableMixin):
  def __eq__(self, other):

    result = (
      isinstance(other, self.__class__)
      and all(
        getattr(self, attr) == getattr(other, attr)
        for attr in self.__slots__
        if attr != 'schema'
      )
    )

    return result

  def __ne__(self, other):
    return not self == other

class UnaryOp(Expr):
  __slots__ = ('expr',)
  def __init__(self, expr):
    self.expr = expr

class NegOp(UnaryOp):
  """ - (expr)"""
  __slots__ = ('expr',)

class NotOp(UnaryOp):
  """ not (expr)"""
  __slots__ = ('expr',)

class ItemGetterOp(Expr):
  """ (expr)[key] """
  __slots__ = ('key',)
  def __init__(self, key):
    self.key = key
  

class BinaryOp(Expr):
  __slots__ = ('lhs', 'rhs')

  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

class And(BinaryOp):
  """lhs and rhs"""
  __slots__ = ('lhs', 'rhs')

class Or(BinaryOp):
  """lhs or rhs"""
  __slots__ = ('lhs', 'rhs')

class LtOp(BinaryOp):
  """Less than"""
  __slots__ = ('lhs', 'rhs')

class LeOp(BinaryOp):
  """Less than or equal to"""
  __slots__ = ('lhs', 'rhs')

class EqOp(BinaryOp):
  """Equal to"""
  __slots__ = ('lhs', 'rhs')

class NeOp(BinaryOp):
  """Not equal to"""
  __slots__ = ('lhs', 'rhs')

class GeOp(BinaryOp):
  """Greater than or equal to"""
  __slots__ = ('lhs', 'rhs')

class GtOp(BinaryOp):
  """Greater than"""
  __slots__ = ('lhs', 'rhs')

class IsOp(BinaryOp):
  """x is y"""
  __slots__ = ('lhs', 'rhs')

class IsNotOp(BinaryOp):
  """x is not y"""
  __slots__ = ('lhs', 'rhs')

class LikeOp(BinaryOp):
  """x LIKE y"""
  __slots__ = ('lhs', 'rhs')

class RLikeOp(BinaryOp):
  """x RLIKE y"""
  __slots__ = ('lhs', 'rhs')

class InOp(BinaryOp):
  """x is y"""
  __slots__ = ('lhs', 'rhs')

class AddOp(BinaryOp):
  """lhs + rhs"""
  __slots__ = ('lhs', 'rhs')

class SubOp(BinaryOp):
  """lhs - rhs"""
  __slots__ = ('lhs', 'rhs')

class MulOp(BinaryOp):
  """lhs * rhs"""
  __slots__ = ('lhs', 'rhs')

class DivOp(BinaryOp):
  """lhs / rhs"""
  __slots__ = ('lhs', 'rhs')


class BetweenOp(BinaryOp):
  """ x between lhs and rhs"""
  __slots__ = ( 'expr', 'lhs', 'rhs')
  def __init__(self, expr, lhs, rhs):
    self.expr = expr
    self.lhs  = lhs
    self.rhs  = rhs

class Const(Expr):
  __slots__ = ('const',)

  def __init__(self, const):
    self.const = const

class NullConst(Const):
  """Null or None"""
  __slots__ = ()
  const = None
  def __init__(self):
    pass


class NumberConst(Const):
  """Integer or Float"""
  __slots__ = ('const',)

class StringConst(Const):
  """A string"""
  __slots__ = ('const',)


class BoolConst(Const):
  """A boolean const"""
  __slots__ = ()
  def __init__(self):
    pass

class TrueConst(BoolConst):
  """The constant True """
  __slots__ = ()
  const=True

class FalseConst(BoolConst):
  """The constant False """
  __slots__ = ()
  const=False


class Var(Expr):
  __slots__ = ('path',)
  def __init__(self, path):
    self.path = path

class Tuple(Expr):
  __slots__ = ('exprs',)
  def __init__(self, *exprs):
    self.exprs = exprs

class Function(Expr):
  __slots__ = ('name', 'args', 'schema', 'func')
  def __init__(self, name, *args, **kw):
    self.name = name
    self.args = args
    self.schema = kw.get('schema')
    self.func = kw.get('func')

  def __call__(self,ctx):
    return self.func(ctx)

  

COMPARISON_OPS = {
  '<'  : LtOp,
  '<=' : LeOp,
  '='  : EqOp,
  '!=' : NeOp,
  '>=' : GeOp,
  '>'  : GtOp,
  'is' : IsOp,
  'is not' : IsNotOp,
  'like' : LikeOp,
  'rlike': RLikeOp
}


MULTIPLICATIVE_OPS ={
  '*'  : MulOp,
  '/'  : DivOp
}

ADDITIVE_OPS = {
  '+'  : AddOp,
  '-'  : SubOp
}

# sql specific expresions

class Asc(UnaryOp):
  """Sort from lowest to highest"""
  __slots__ = ('expr',)
  
class Desc(UnaryOp):
  """Sort from highest to lowest """
  __slots__ = ('expr',)


class ParamGetterOp(UnaryOp):
  """ ?<number> """
  __slots__ = ('expr',)
  

class SelectAllExpr(Expr):
  __slots__ = ('table',)

  def __init__(self, table=None):
    self.table = table

class RenameOp(Expr):
  __slots__ = ('name','expr')

  def __init__(self, name, expr):
    self.name = name
    self.expr  = expr



class RelationalOp(Expr):
  pass

class LoadOp(RelationalOp):
  """Load a relation with the given name"""
  __slots__ = ('name','schema')
  def __init__(self, name, schema=None):
    self.name = name
    self.schema = schema

class AliasOp(RelationalOp):
  """Rename the relation to the given name"""
  __slots__ = ('relation', 'name', 'schema')
  def __init__(self, name, relation, schema=None):
    self.name = name
    self.relation = relation
    self.schema = schema




class ProjectionOp(RelationalOp):
  __slots__ = ('relation', 'exprs', 'schema')
  def __init__(self, relation, *exprs, **kw):
    self.relation = relation
    self.exprs = exprs
    self.schema = kw.get('schema')

class SelectionOp(RelationalOp):
  __slots__ = ('relation','bool_op','schema')
  def __init__(self, relation, bool_op, schema=None):
    self.relation = relation
    self.bool_op = bool_op
    self.schema = schema

class CaseWhenOp(RelationalOp):
  __slots__ = ('conditions', 'default_value')
  def __init__(self, conditions, default_value):
    self.conditions = conditions
    self.default_value = default_value

class CastOp(RelationalOp):
  __slots__ = ('value', 'type')
  def __init__(self, value, type):
    self.value = value
    self.type = type


class BinRelationalOp(RelationalOp):
  """
  RelationalOp that operates on two relations
  """
  __slots__ = ('left', 'right', 'schema')

class UnionAllOp(BinRelationalOp):
  """Combine the results of multiple operations with identical schemas
  into one.
 """
  __slots__ = ('left', 'right', 'schema')
  def __init__(self, left, right, schema=None):
    self.left = left
    self.right = right
    self.schema = schema


class JoinOp(BinRelationalOp):
  __slots__ = ('left','right', 'bool_op', 'schema')
  def __init__(self,  left, right, bool_op = TrueConst(), schema=None):
    self.left = left
    self.right = right
    self.bool_op = bool_op
    self.schema = schema

class LeftJoinOp(JoinOp):
  __slots__ = ('left','right', 'bool_op', 'schema')

class OrderByOp(RelationalOp):
  __slots__ = ('relation', 'exprs', 'schema')
  def __init__(self, relation, first, *exprs, **kw):
    self.relation = relation
    self.exprs = (first,) + exprs
    self.schema = kw.get('schema')

  def new(self, **parts):
    # OrderByOp's __init__ doesn't match what's defined in __slots__
    # so we have to help it make a copy of this object
    exprs = parts.pop('exprs', self.exprs)
    first = exprs[0]
    tail = exprs[1:]
    relation = parts.pop('relation', self.relation)

    return self.__class__(relation, first, *tail, **parts)


class GroupByOp(RelationalOp):
  __slots__ = ('relation','aggregates','exprs','schema')
  def __init__(self, relation,  *exprs, **kw):
    self.relation   = relation
    self.exprs      = exprs

    # bit of a kludge, aggregates can't be resolved at
    # parse time, so they start as an empty list and
    # are set when the expression tree is evaluated.
    # See compilers.local.projection_op for details
    self.aggregates = kw.get('aggregates', ())

    self.schema = kw.get('schema')

class SliceOp(RelationalOp):
  __slots__ = ('relation','start','stop', 'schema')
  def __init__(self, relation, *args, **kw):
    self.relation = relation
    if len(args) == 1:
      self.start = 0
      self.stop = args[0]
    else:
      self.start, self.stop = args

    self.schema = kw.get('schema')

  def new(self, **parts):
    # slice op's __init__ doesn't match what's defined in __slots__
    # so we have to help it make a copy of this object
    args = parts.pop('start', self.start), parts.pop('stop', self.stop)
    relation = parts.pop('relation', self.relation)
 
    return self.__class__(relation, *args, **parts)

    
