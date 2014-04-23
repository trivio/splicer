import operator
from functools import partial
from itertools import islice

from ..ast import *

from ..operations import  walk, visit_with, isa
from ..schema_interpreter import (
  field_from_expr,  JoinSchema, relational_function
)


def compile(query):
  # resolve views and schemas

  return walk(
    query.operations, 
    visit_with(
      query.dataset,      
      (isa(LoadOp), load_relation),
      (isa(ProjectionOp), ensure_group_op_when_ags),
      (isa_op, relational_op),
      (is_callable, validate_function)
    )
  )


def isa_op(loc):
  return type(loc.node()) in RELATION_OPS

def relational_op(dataset, loc, operation):
  func = RELATION_OPS[type(operation)](dataset,  operation)
  func.schema = operation.schema
  return loc.replace(func)

def load_relation(dataset, loc, operation):
  adapter = dataset.adapter_for(operation.name)
  return adapter.evaluate(loc)

def is_callable(loc):
  return callable(loc.node())

def validate_function(dataset, loc, function):
  """
  Simple validation which ensure that nodes have been
  compiled to functions have a schema attribute set.
  """
  assert hasattr(function, 'schema'), (
    "{} must have a schema attribute".format(function)
  )
  return loc

def alias_op(dataset, operation):
  def alias(ctx):
    relation = operation.relation(ctx)
    return relation

  return alias


def ensure_group_op_when_ags(dataset, loc, operation):
  aggs = aggregates(operation.exprs, dataset)
  if aggs:
    # we have an aggregate operations, push them up to the group by
    # operation or add a group by operation if all projection expresions
    # are aggregates
    u = loc.up()
    parent_op = u and u.node()
    if not isinstance(parent_op, GroupByOp):
      if len(aggs) != len(operation.exprs):
        raise group_by_error(operation.expresions, aggs)
      loc = loc.replace(GroupByOp(operation, aggregates=aggs)).down()
    else:
      loc = u.replace(parent_op.new(aggregates=aggs)).down()
  return loc


def projection_op(dataset,  operation):
  schema = operation.relation.schema
  columns = tuple([
    column
    for group in [
      column_expr(expr, schema, dataset)
      for expr in operation.exprs
    ]
    for column in group
  ])


  def projection(ctx):
    relation = operation.relation(ctx)
 
    return (
      tuple( col(row, ctx) for col in columns )
      for row in relation
    )
    
  return projection



def selection_op(dataset, operation):

  if operation.bool_op is None:
    return lambda relation, ctx: relation

  predicate  = value_expr(operation.bool_op, operation.schema, dataset)

  def selection(ctx):
    relation = operation.relation(ctx)

    return (
      row
      for row in relation
      if predicate(row, ctx)
    )
    
  return selection

def join_op(dataset, operation):
  left  = operation.left
  right = operation.right

  schema = JoinSchema(left.schema, right.schema) 
  try:
    comparison = join_keys(left.schema, right.schema, operation.bool_op)
    method = hash_join
  except ValueError:
    # icky cross product
    comparison = value_expr(operation.bool_op, schema, dataset)
    method = nested_block_join

  def join(ctx):
    left = operation.left(ctx)
    right = operation.right(ctx)


    return method(operation.left, operation.right, comparison, ctx)
    
  return join



def order_by_op(dataset, operation):
  columns = tuple(
    value_expr(expr, operation.relation.schema, dataset)
    for expr in operation.exprs
  )  
  schema = operation.schema

  def order_by(ctx):
    relation = operation.relation(ctx)

    def key(row):
      return tuple(c(row, ctx) for c in columns)

    return sorted(relation, key=key)
    
  return order_by

def group_by_op(dataset, group_op):

  if group_op.exprs:
    load   = order_by_op(dataset, group_op)
    load.schema = group_op.schema
  else:
    # we're aggregating the whole table
    load = group_op.relation 


  exprs      = group_op.exprs
  aggs       = group_op.aggregates

  initialize = initialize_op(aggs)
  accumalate = accumulate_op(aggs)
  finalize   = finalize_op(aggs)

  if group_op.exprs:
    key = key_op(group_op.exprs, load.schema)
  else:
    # it's all aggregates with no group by elements
    # so no need to order the table
    key = lambda row,ctx: None


  def group_by(ctx):
    ordered_relation = load(ctx)

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

    return group()
    
  return group_by


def slice_op(dataset, expr):
  def limit(ctx):
    relation = expr.relation(ctx)
    return islice(relation, expr.start, expr.stop)
    
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

def group_by_error(exprs, aggs):
  """Used to raise an error highlighting the first
  offending column when a projection operation has a mix of
  aggregate expresions and non-aggregate expresions but no 
  group by.

  """

  agg_expr = dict(aggs)
  for col, expr in enumerate(exprs):
    if col not in aggs:
      return SyntaxError(
        (
          '"{}" must appear in the GROUP BY clause '
          'or be used in an aggregate function'
        ).format(expr)
      )


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


def column_expr(expr, schema, dataset):
  # selectall returns a group of expresions, group solo to be flattened
  # by the outer loop

  if isinstance(expr, SelectAllExpr):
    return select_all_expr(expr, schema, dataset)
  else: 
    return (value_expr(expr,schema,dataset),)

def select_all_expr(expr, schema, dataset):

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
    var_expr(Var(f.name), schema, dataset) for f in fields
  ]

def value_expr(expr, schema, dataset):
  return VALUE_EXPR[type(expr)](expr, schema, dataset)

def itemgetter_expr(expr, schema, dataset):
  key = expr.key
  def itemgetter(row, ctx):
    return row[key]
  return itemgetter

def sub_expr(expr, schema, dataset):
  return value_expr(expr.expr, schema, dataset)

def var_expr(expr, schema, dataset):
  pos = schema.field_position(expr.path)
  def var(row, ctx):
    return row[pos]
  return var

def const_expr(expr, schema, dataset):
  def const(row, ctx):
    return expr.const
  return const

def null_expr(expr, schema, dataset):
  return lambda row, ctx: None

def function_expr(expr, schema, dataset):
  function = dataset.get_function(expr.name)
  arg_exprs = tuple(
    value_expr(arg_expr, schema, dataset)
    for arg_expr in expr.args
  )

  def _(row, ctx):
    args = tuple(
      arg_expr(row, ctx)
      for arg_expr in arg_exprs
    )
    return function(*args)

  _.__name__ = str(expr.name)
  return _



def desc_expr(expr, schema, dataset):
  field = field_from_expr(expr.expr, dataset, schema)
  value = value_expr(expr.expr, schema, dataset)

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
 
def unary_op(operator, expr, schema, dataset):
  val = value_expr(expr.expr, schema, dataset)
  def _(row,ctx):
    return operator(val(row, ctx))
  _.__name__ = operator.__name__
  return _

def binary_op(operator, expr, schema, dataset):
  lhs = value_expr(expr.lhs, schema, dataset)
  rhs = value_expr(expr.rhs, schema, dataset)

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
  ProjectionOp: projection_op,
  SelectionOp: selection_op,
  OrderByOp: order_by_op,
  GroupByOp: group_by_op,
  SliceOp: slice_op,
  JoinOp: join_op,
  Function: relational_function,
  
}

# sigh, oh python and your circular import
from .join import nested_block_join, hash_join, join_keys
