# schema_interpreter.py
"""
Module used to interpret the AST into a schema based on a given relation.
"""

from . import Relation
from .schema import Schema,JoinSchema
from .operations import walk, visit_with, is_not

from .field import Field
from .ast import (
  ProjectionOp, SelectionOp, GroupByOp, RenameOp, LoadOp,
  JoinOp,
  Var, Function, 
  Const, UnaryOp, BinaryOp, AliasOp, SelectAllExpr,
  NumberConst, StringConst, BoolConst
)


def resolve_schema(dataset, operations, *additional_visitors):
  """
  Given an expresion tree return a new tree whose node's
  schema values are properly set.
  """

  visitors = additional_visitors + (
    (is_not(Relation), resolve_schema_for_node),
  )

  return walk(
    operations,
    visit_with(
      dataset,
      *visitors
    )
  )



def resolve_schema_for_node(dataset, loc, op):
  dispatch = op_type_to_schemas.get(
    type(op),
    update_op(schema_from_relation)
  )
 
  # each dispatch will return an operation that will
  # replace the current node. The operation may
  # simply be updated with a new schema, or it could
  # be relpaced with a new subtree, or function
  return loc.replace(dispatch(op, dataset))


def schema_from_relation(operation, dataset):
  """
  Return the schema from the relation's child, this is the default
  method for any relation operation that doesn't modify the schema
  """
  return operation.relation.schema




# Todo:
# Function -> Relation(Schema, (context-> [Tuples]))
def schema_from_function_op(operation, dataset):
  func = dataset.get_function(operation.name)

  if hasattr(func, 'resolve'):
    return func.resolve(dataset)

  if callable(func.returns):
    #schema = operation.args[0].schema

    args = [
      a if hasattr(a,'schema') else a.const
      for a in operation.args
    ]

    schema = func.returns(*args)

  else:
    schema = func.returns

  def records(ctx):
    return func(ctx, *args)


  return Relation(None, operation.name, schema, records)

def relational_function(dataset, op):
  """Invokes a function that operates on a whole relation"""
  return op.func
  function = dataset.get_function(op.name)

  args = []
  for arg_expr in op.args:
    if isinstance(arg_expr, Const):
      #args.append(lambda ctx, const=arg_expr.const: const)
      args.append(arg_expr.const)
    elif isinstance(arg_expr, Relation):
      #def c(ctx, f=arg_expr):
      #  import pdb; pdb.set_trace()
      #  return  f.schema,f(ctx)
      #c.__name__ = arg_expr.schema.name

      args.append(arg_expr)
    else:
      raise ValueError(
        "Only Relational Operations and constants "
        "are allowed in table functions"
      )

  def invoke(ctx):
    return function(ctx, *args)
  return invoke




def schema_from_load(operation, dataset):

  return dataset.get_schema(operation.name)
  #return dataset.get_relation(operation.name).schema

def schema_from_projection_op(projection_op, dataset):
  """
  Given a projection_op, datset and existing schema, return the new
  schema.
  """

  schema = projection_op.relation.schema

  fields = [
    field
    for expr in projection_op.exprs
    for field in fields_from_expr(expr,dataset,schema)
  ]

  return Schema(fields)


def schema_from_join_op(join_op, dataset):
  left  =  join_op.left.schema
  right =  join_op.right.schema

  return JoinSchema(left,right)


def schema_from_alias_op(alias_op, dataset):
  schema = alias_op.relation.schema
  return schema.new(name=alias_op.name)


def fields_from_expr(expr, dataset, schema):
  if isinstance(expr, SelectAllExpr):
    for field in fields_from_select_all(expr, dataset, schema):
      yield field
  else:
    yield field_from_expr(expr, dataset, schema)


def field_from_expr(expr, dataset, schema):
  """
  """
  expr_type = type(expr)
  if expr_type == Var:
    return field_from_var(expr, schema)
  elif issubclass(expr_type, Const):
    return field_from_const(expr)
  elif expr_type == Function:
    return field_from_function(expr, dataset, schema)
  elif expr_type == RenameOp:
    return field_from_rename_op(expr, dataset, schema)
  elif issubclass(expr_type, UnaryOp):
    field = field_from_expr(expr.expr, dataset, schema)
    return field.new(name="{0}({1})".format(expr_type.__name__, field.name))
  elif issubclass(expr_type, BinaryOp):
    lhs_field = field_from_expr(expr.lhs, dataset, schema)
    rhs_field = field_from_expr(expr.lhs, dataset, schema)
    if lhs_field.type != rhs_field.type:
      raise ValueError(
        "Can't coerce {} to {}".format(lhs_fielt.type, rhs_field.type)
      )
    else:
      return lhs_field.new(name="?column?".format(
        expr_type.__name__, 
        lhs_field.name,
        rhs_field.name
      ))



def fields_from_select_all(expr, dataset, schema):
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
    field_from_var(Var(f.name), schema) for f in fields
  ]


def field_from_const(expr):
  return Field(
    name ='?column?',
    type = {
      NumberConst: 'INTEGER',
      StringConst: 'STRING',
      BoolConst: 'BOOLEAN'
    }[type(expr)]
  )


def field_from_var(var_expr, schema):
  return schema[var_expr.path]


def field_from_function(function_expr, dataset, schema):
  name = function_expr.name
  function = dataset.get_function(function_expr.name)

  if function.returns:
    return function.returns
  #elif len(function_expr.args):
  #  # no return type specified guess the type based on the first
  #  # argument. Dataset.add_function should prevent functions
  #  # from being registered without args and return_types
  #  return field_from_expr(function_expr.args[0], dataset, schema)
  else:
    raise ValueError("Can not determine return type of Function {}".format(name))


def field_from_rename_op(expr, dataset, schema):
  field = field_from_expr(expr.expr, dataset, schema)
  return field.new(name=expr.name)

def replace_schema(op, schema):
  return op.new(schema=schema)

# :: (operation -> dataset -> schema) -> (operation, dataset) -> RelationalOp|(callable)
def update_op(func):
  """
  Adapts functions that return schemas to return operations.

  Takes a function that returns a schema given an operation and a dataset.
  Returns a function that when called with an operation and dataset returns
  a new operation with the coresponding schema.
  """
  def _(operation, dataset):
    schema = func(operation, dataset)
    return replace_schema(operation, schema)
  return _


op_type_to_schemas = {
  LoadOp: update_op(schema_from_load),
  ProjectionOp: update_op(schema_from_projection_op),
  AliasOp: update_op(schema_from_alias_op),
  JoinOp: update_op(schema_from_join_op),
  Function: schema_from_function_op,

}