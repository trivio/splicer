import operator
from functools import partial
from itertools import islice

from ..ast import *
from ..aggregate import Aggregate
from ..relation import Relation
from ..schema_interpreter import field_from_expr, schema_from_projection_op

def compile(query):
  plan = query.operations
  operations = tuple(
    relational_op(op, query.dataset)
    for op in plan
  )

  def evaluate(ctx, *params):
    relation = ctx['dataset'].get_relation(query.relation_name)

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
    schema = schema_from_projection_op(operation, dataset, relation.schema)
    return Relation(
      schema,
      (
        tuple( col(row, ctx) for col in columns )
        for row in relation
      )
    )

  return projection



def selection_op(operation, dataset):
  if operation.bool_op is None:
    return lambda relation, ctx: relation


  def selection(relation, ctx):
    predicate  = value_expr(operation.bool_op, relation, dataset)
    return Relation(
      relation.schema,
      (
        row
        for row in relation
        if predicate(row, ctx)
      )
    )
  return selection

def order_by_op(operation, dataset):

  def order_by(relation, ctx):
    columns = tuple(
      value_expr(expr, relation, dataset)
      for expr in operation.exprs
    )  

    def key(row):
      return tuple(c(row, ctx) for c in columns)

    return Relation(
      relation.schema, 
      iter(sorted(relation, key=key))
    )
  return order_by

def group_by_op(operation, dataset):

  order_by   = order_by_op(operation, dataset) 
  projection = projection_op(operation.projection_op, dataset)


  exprs      = operation.projection_op.exprs

  aggs       = aggregates(exprs, dataset)

  initialize = initialize_op(aggs)
  accumalate = accumulate_op(aggs)
  finalize   = finalize_op(aggs)


  def group_by(relation, ctx):
    if operation.exprs:
      ordered_relation = order_by(projection(relation, ctx), ctx)
      key = key_op(operation.exprs, ordered_relation.schema)
    else:
      # it's all aggregates with no group by elements
      # so no need to order the table
      ordered_relation = projection(relation, ctx)
      key = lambda row,ctx: None

    schema = schema_from_projection_op(
      operation, 
      dataset, 
      ordered_relation.schema
    )

    def group():
      records = iter(ordered_relation)

      row = records.next()
      group = key(row, ctx)
      
      record = accumalate(initialize(row), row)

      for row in records:
        next = key(row, ctx)
        if next != group:
          yield finalize(record)
          group = next
          record = initialize(row)
        previous_row = accumalate(record, row)

      yield finalize(record)

    return Relation(
      schema,
      group()
    )
  return group_by



def slice_op(expr, dataset):

  def limit(relation, ctx):
    return Relation(
      relation.schema,
      islice(relation, expr.start, expr.stop)
    )
  return limit

def is_aggregate(expr, dataset):
  """Returns true if the expr is an aggregate function."""
  if isinstance(expr, RenameOp):
    expr = expr.expr

  return isinstance(expr, Function) and expr.name in dataset.aggregates

def aggregate_expr(expr, dataset):
  if isinstance(expr, RenameOp):
    expr = expr.expr

  return dataset.aggregates[expr.name]


def key_op(exprs, schema):
  positions = tuple(
    schema.field_position(expr.path)
    for expr in exprs
  )
      
  def key(row, ctx):
    return tuple(row[pos] for pos in positions)
  return key

def initialize_op(pos_and_aggs):
  def initialize(row):
    # convert the tuple to a list so we can modify it
    record = list(row)
    for pos, agg in pos_and_aggs:
      record[pos] = agg.initial
    return record
  return initialize

def accumulate_op(pos_and_aggs):
  def accumulate(record, row):
    for pos, agg in pos_and_aggs:
      args = row[pos]
      state = record[pos]
      record[pos] = agg.function(state, *args)
    return record
  return accumulate

def finalize_op(pos_and_aggs):
  def finalize(record):
    # convert the tuple to a list so we can modify it
    for pos, agg in pos_and_aggs:
      if agg.finalize:
        state = record[pos]
        record[pos] = agg.function(state, *args)
    return tuple(record)
  return finalize



def aggregates(exprs, dataset):
  """Returns a list of list or the aggregates in the exprs.

  The first item is the column index of the aggregate the
  second is the aggregate itself.
  """
  return tuple(
    (pos, aggregate_expr(aggr, dataset))
    for pos, aggr in enumerate(exprs)
    if is_aggregate(aggr, dataset)
  )


def value_expr(expr, relation, dataset):
  return VALUE_EXPR[type(expr)](expr, relation, dataset)

def itemgetter_expr(expr, relation, dataset):
  key = expr.key
  def itemgetter(row, ctx):
    return row[key]
  return itemgetter

def sub_expr(expr, relation, dataset):
  return value_expr(expr.expr, relation, dataset)

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
  function = dataset.get_function(expr.name)
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

  _.__name__ = expr.name
  return _



def desc_expr(expr, relation, dataset):
  field = field_from_expr(expr.expr, dataset, relation.schema)
  value = value_expr(expr.expr)

  if field.type in ("INTEGER", "FLOAT", "DOUBLE"):

    def invert_number(record, ctx):
      return -value(record,ctx)

    return invert_number

  elif field.type == "STRING":
    def invert_string(record, ctx):
      return [-b for b in bytearray(value(record,ctx))]
    return invert_string
  else:
    return lambda r,c: None
 
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

  RenameOp: sub_expr,
  NullConst: null_expr,

  Asc: sub_expr,
  Desc: desc_expr



}

RELATION_OPS = {
  ProjectionOp: projection_op,
  SelectionOp: selection_op,
  OrderByOp: order_by_op,
  GroupByOp: group_by_op,
  SliceOp: slice_op
  
}