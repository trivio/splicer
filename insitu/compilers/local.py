import operator
from functools import partial
from ..ast import *

def compile(query):
  operations = tuple(
    relational_op(op, query.dataset)
    for op in query.operations
  )

  def evaluate(ctx, *params):
    relation = query.relation
    for op in operations:
      relation = op(relation, ctx)
    return relation

  return evaluate


def relational_op(operation, dataset):
  return RELATION_OPS[type(operation)](operation, dataset)


def projection_op(operation, dataset):

  def projection(relation, ctx):
    columns = tuple(
      value_expr(expr, relation, dataset)
      for expr in operation.exprs
    )

    return (
      tuple(col(row, ctx) for col in columns )
      for row in relation
    )
  return projection

def selection_op(operation, dataset):
  if operation.bool_op is None:
    return lambda relation, ctx: relation


  def selection(relation, ctx):
    predicate  = value_expr(operation.bool_op, relation, dataset)
    return (
      row
      for row in relation
      if predicate(row, ctx)
    )
  return selection

def value_expr(expr, relation, dataset):
  return VALUE_EXPR[type(expr)](expr, relation, dataset)

def itemgetter_expr(expr, relation, dataset):
  key = expr.key
  def itemgetter(row, ctx):
    return row[key]
  return itemgetter

def rename_op(expr, relation, dataset):
  return columne_expr(expr.expr, relation, dataset)

def var_expr(expr, relation, dataset):
  pos = relation.schema.field_position(expr.path)
  def var(row, ctx):
    return row[pos]
  return var

def const_expr(expr, relation, dataset):
  def const(row, ctx):
    return expr.const
  return const

def null_expr(expr, relation, dataset):
  return lambda row, ctx: None

def function_expr(expr, relation, dataset):
  function = dataset.udf(expr.name)
  arg_exprs = tuple(
    value_expr(arg_expr, relation, dataset)
    for arg_expr in expr.args
  )

  def _(row, ctx):
    args = tuple(
      arg_expr(row, ctx)
      for arg_expr in arg_exprs
    )
    return function(*args)

  _.__name__ = function.__name__
  return _

def unary_op(operator, expr, relation, dataset):
  val = value_expr(expr.expr, relation, dataset)
  def _(row,ctx):
    return operator(val(row, ctx))
  _.__name__ = operator.__name__
  return _

def binary_op(operator, expr, relation, dataset):
  lhs = value_expr(expr.lhs, relation, dataset)
  rhs = value_expr(expr.rhs, relation, dataset)

  def _(row, ctx):
    return operator(lhs(row, ctx), rhs(row, ctx))
  _.__name__ = operator.__name__
  return _



VALUE_EXPR = {
  Var: var_expr,
  StringConst: const_expr,
  NumberConst: const_expr,
  Function: function_expr,

  NegOp: partial(unary_op, operator.neg),
  NotOp: partial(unary_op, operator.not_),

  And: partial(binary_op, operator.and_),
  Or: partial(binary_op, operator.or_),

  LtOp: partial(binary_op, operator.lt),
  LeOp: partial(binary_op, operator.le),
  EqOp: partial(binary_op, operator.eq),
  NeOp: partial(binary_op, operator.ne),
  GeOp: partial(binary_op, operator.ge),
  GtOp: partial(binary_op, operator.gt),

  AddOp: partial(binary_op, operator.add),
  SubOp: partial(binary_op, operator.sub),

  MulOp: partial(binary_op, operator.mul),
  DivOp: partial(binary_op, operator.div),

  ItemGetterOp: itemgetter_expr,

  RenameOp: rename_op,
  NullConst: null_expr


}

RELATION_OPS = {
  ProjectionOp: projection_op,
  SelectionOp: selection_op
}