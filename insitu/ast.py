class Exp(object):
  pass

class UnaryOp(Exp):
  def __init__(self, exp):
    self.exp = exp

class NegOp(UnaryOp):
  """ - (exp)""" 

class NotOp(UnaryOp):
  """ not (exp)""" 

class ItemGetterOp(UnaryOp):
  """ (exp)[exp] """
  

class BinaryOp(Exp):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

class And(BinaryOp):
  """lhs and rhs"""

class Or(BinaryOp):
  """lhs or rhs"""

class LtOp(BinaryOp):
  """Less than"""
  pass

class LeOp(BinaryOp):
  """Less than or equal to"""

class EqOp(BinaryOp):
  """Equal to"""

class NeOp(BinaryOp):
  """Not equal to"""

class GeOp(BinaryOp):
  """Greater than or equal to"""

class GtOp(BinaryOp):
  """Greater than"""

class AddOp(BinaryOp):
  """lhs + rhs"""

class SubOp(BinaryOp):
   """lhs - rhs"""

class MulOp(BinaryOp):
  """lhs * rhs"""

class DivOp(BinaryOp):
   """lhs / rhs"""

class Const(Exp):
  def __init__(self, const):
    self.const = const

class NumberConst(Const):
  """Integer or Float"""

class StringConst(Const):
  """A string"""

class Var(Exp):
  def __init__(self, path):
    self.path = path

class TupleExp(Exp):
  def __init__(self, *exps):
    self.exps = exps

class FunctionExp(Exp):
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

class ParamGetterOp(UnaryOp):
  """ ?<number> """
  

class SelectAllExp(Exp):
  def __init__(self, table=None):
    self.table = table

class RenameOp(Exp):
  def __init__(self, name, exp):
    self.name = name
    self.exp  = exp


class ProjectionOp(Exp):
  def __init__(self, *exprs):
    self.exprs = exprs


class SelectionOp(Exp):
  def __init__(self, bool_op):
    self.bool_op = bool_op
