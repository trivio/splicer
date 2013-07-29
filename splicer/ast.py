class Expr(object):
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


class NullConst(Expr):
  """Null or None"""
  __slots__ = ()

class Const(Expr):
  __slots__ = ('const',)

  def __init__(self, const):
    self.const = const

class NumberConst(Const):
  """Integer or Float"""
  __slots__ = ('const',)

class StringConst(Const):
  """A string"""
  __slots__ = ('const',)

class Var(Expr):
  __slots__ = ('path',)
  def __init__(self, path):
    self.path = path

class Tuple(Expr):
  __slots__ = ('exps',)
  def __init__(self, *exps):
    self.exps = exps

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

class ProjectionOp(Expr):
  __slots__ = ('exprs',)
  def __init__(self, *exprs):
    self.exprs = exprs

class SelectionOp(Expr):
  __slots__ = ('bool_op',)
  def __init__(self, bool_op):
    self.bool_op = bool_op

class OrderByOp(Expr):
  __slots__ = ('exprs',)
  def __init__(self, first, *exprs):
    self.exprs = (first,) + exprs

class GroupByOp(Expr):
  __slots__ = ('exprs','projection_op')
  def __init__(self, projection_op, *exprs):
    self.projection_op = projection_op
    self.exprs =  exprs

class SliceOp(Expr):
  __slots__ = ('start','stop')
  def __init__(self, *args):
    if len(args) == 1:
      self.start = 0
      self.stop = args[0]
    else:
      self.start, self.stop = args
    
