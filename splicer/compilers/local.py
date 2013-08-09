import operator
from functools import partial
from itertools import islice

from ..ast import *
from ..aggregate import Aggregate
from ..relation import Relation
from ..operations import replace_views
from ..schema_interpreter import (
  field_from_expr, schema_from_projection_op, schema_from_join_op
)


def compile(query):

  operations = replace_views(query.operations, query.dataset)

  plan = relational_op(operations, query.dataset)

  def evaluate(ctx, *params):
    return plan(ctx)

  return evaluate



def load_op(operation, dataset):
  def load(ctx):
    return dataset.get_relation(operation.name)
  return load

def alias_op(operation, dataset):
  load = relational_op(operation.relation, dataset)

  def alias(ctx):
    relation = load(ctx)
    return Relation(
      relation.schema.new(name=operation.name),
      iter(relation)
    )

  return alias

def relational_op(operation, dataset):
  return RELATION_OPS[type(operation)](operation, dataset)

def projection_op(operation, dataset):
  load = relational_op(operation.relation, dataset)

  def projection(ctx):
    relation = load(ctx)
    columns = tuple([
      column
      for group in [
        column_expr(expr, relation, dataset)
        for expr in operation.exprs
      ]
      for column in group
    ])

    schema = schema_from_projection_op(operation, dataset)
    return Relation(
      schema,
      (
        tuple( col(row, ctx) for col in columns )
        for row in relation
      )
    )

  return projection



def selection_op(operation, dataset):
  load = relational_op(operation.relation, dataset)

  if operation.bool_op is None:
    return lambda relation, ctx: relation


  def selection(ctx):
    relation = load(ctx)
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

def join_op(operation, dataset):
  right_op = relational_op(operation.right, dataset)
  left_op = relational_op(operation.left, dataset)

  def join(ctx):
    left = left_op(ctx)
    right = right_op(ctx)

    schema = schema_from_join_op(operation, dataset)

    # seems silly to have to build a fake relation
    # just so var_expr (which is reached by value_expr)
    # can use the new schema. value_expr should just
    # take the schema as an arg...
    bogus = Relation(schema, None)


    try:
      comparison = join_keys(left, right, operation.bool_op)
      method = hash_join
    except ValueError:
      # icky cross product
      comparison = value_expr(operation.bool_op, bogus, dataset)
      method = nested_block_join


    return Relation(
      schema,
      method(left_op, right_op, comparison, ctx)
    )


  return join



def order_by_op(operation, dataset):
  load = relational_op(operation.relation, dataset)
  def order_by(ctx):
    relation = load(ctx)

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
  if operation.exprs:
    load   = order_by_op(operation, dataset)
  else:
    load = relational_op(operation.relation, dataset)


  exprs      = operation.relation.exprs

  aggs       = aggregates(exprs, dataset)

  initialize = initialize_op(aggs)
  accumalate = accumulate_op(aggs)
  finalize   = finalize_op(aggs)


  def group_by(ctx):
    ordered_relation = load(ctx)
    if operation.exprs:
      key = key_op(operation.exprs, ordered_relation.schema)
    else:
      # it's all aggregates with no group by elements
      # so no need to order the table
      key = lambda row,ctx: None

    schema = schema_from_projection_op(
      operation, 
      dataset
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
  load = relational_op(expr.relation, dataset)
  def limit(ctx):
    relation = load(ctx)
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


def column_expr(expr, relation, dataset):
  # selectall returns a group of expresions, group solo to be flattened
  # by the outer loop

  if isinstance(expr, SelectAllExpr):
    return select_all_expr(expr, relation, dataset)
  else: 
    return (value_expr(expr,relation,dataset),)

def select_all_expr(expr, relation, dataset):
  schema = relation.schema
  if expr.table is None:
    fields = schema.fields
  else:
    prefix = expr.table + "."
    fields = [
      f
      for f in schema.fields
      if f.name.startswith(prefix)
    ]

  return [
    var_expr(Var(f.name), relation, dataset) for f in fields
  ]

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

  NullConst: const_expr,
  TrueConst: const_expr,
  FalseConst: const_expr,

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
  IsOp: partial(binary_op, operator.is_),
  IsNotOp: partial(binary_op, operator.is_not),

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
  AliasOp: alias_op,
  LoadOp: load_op,
  ProjectionOp: projection_op,
  SelectionOp: selection_op,
  OrderByOp: order_by_op,
  GroupByOp: group_by_op,
  SliceOp: slice_op,
  JoinOp: join_op
  
}

# sigh, oh python and your circular import
from .join import nested_block_join, hash_join, join_keys
