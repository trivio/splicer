from .immutable import ImmutableMixin

class Expr(ImmutableMixin):
  def __eq__(self, other):

    result = (
      isinstance(other, self.__class__)
      and all(
        getattr(self, attr) == getattr(other, attr)
        for attr in self.__slots__
      )
    )

    return result

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
  __slots__ = ('name', 'args')
  def __init__(self, name, *args):
    self.name = name
    self.args = args

  

COMPARISON_OPS = {
  '<'  : LtOp,
  '<=' : LeOp,
  '='  : EqOp,
  '!=' : NeOp,
  '>=' : GeOp,
  '>'  : GtOp,
  'is' : IsOp,
  'is not' : IsNotOp
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
  __slots__ = ('name',)
  def __init__(self, name):
    self.name = name

class AliasOp(RelationalOp):
  """Rename the relation to the given name"""
  __slots__ = ('relation', 'name')
  def __init__(self, name, relation):
    self.name = name
    self.relation = relation


class ProjectionOp(RelationalOp):
  __slots__ = ('relation', 'exprs')
  def __init__(self, relation, *exprs):
    self.relation = relation
    self.exprs = exprs

class SelectionOp(RelationalOp):
  __slots__ = ('relation','bool_op',)
  def __init__(self, relation, bool_op):
    self.relation = relation
    self.bool_op = bool_op

class JoinOp(RelationalOp):
  __slots__ = ('left','right', 'bool_op')
  def __init__(self,  left, right, bool_op = TrueConst()):
    self.left = left
    self.right = right
    self.bool_op = bool_op


class OrderByOp(RelationalOp):
  __slots__ = ('relation', 'exprs')
  def __init__(self, relation, first, *exprs):
    self.relation = relation
    self.exprs = (first,) + exprs

  def new(self, **parts):
    # OrderByOp's __init__ doesn't match what's defined in __slots__
    # so we have to help it make a copy of this object
    exprs = parts.get('exprs', self.exprs)
    first = exprs[0]
    tail = exprs[1:]
    relation = parts.get('relation', self.relation)

    return self.__class__(relation, first, *tail)


class GroupByOp(RelationalOp):
  __slots__ = ('exprs','relation')
  def __init__(self, relation, *exprs):
    self.relation = relation
    self.exprs =  exprs

class SliceOp(RelationalOp):
  __slots__ = ('relation','start','stop')
  def __init__(self, relation, *args):
    self.relation = relation
    if len(args) == 1:
      self.start = 0
      self.stop = args[0]
    else:
      self.start, self.stop = args

  def new(self, **parts):
    # slice op's __init__ doesn't match what's defined in __slots__
    # so we have to help it make a copy of this object
    args = parts.get('start', self.start), parts.get('stop', self.stop)
    relation = parts.get('relation', self.relation)

    return self.__class__(relation, *args)

    
