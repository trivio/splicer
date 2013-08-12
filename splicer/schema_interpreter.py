# schema_interpreter.py
"""
Module used to interpret the AST into a schema based on a given relation.
"""

from .operations import replace_views
from .schema import Schema,JoinSchema

from .field import Field
from .ast import (
  ProjectionOp, SelectionOp, GroupByOp, RenameOp, LoadOp,
  JoinOp,
  Var, Function, 
  Const, UnaryOp, BinaryOp, AliasOp, SelectAllExpr,

  NumberConst, StringConst, BoolConst
)

def interpret(dataset, operations):
  """
  Returns the schema that will be produced if the given
  operations are applied to the starting schema.
  """

  # todo, consider pushing this up into the dataset
  # object as it maybe duplicated in the complie step
  # as well
  operations = replace_views(operations, dataset)
  op_type = type(operations)
  dispatch = op_type_to_schemas.get(
    op_type,
    schema_from_relation
  ) 

  return dispatch(operations, dataset)


def schema_from_relation(operation, dataset):
  return interpret(dataset, operation.relation)

def schema_from_load(operation, dataset):
  return dataset.get_relation(operation.name).schema

def schema_from_projection_op(projection_op, dataset):
  """
  Given a projection_op, datset and existing schema, return the new
  schema.
  """

  schema = interpret(dataset, projection_op.relation)

  fields = [
    field
    for expr in projection_op.exprs
    for field in fields_from_expr(expr,dataset,schema)
  ]

  
  return Schema(fields)

def schema_from_join_op(join_op, dataset):
  left = interpret(dataset, join_op.left)
  right = interpret(dataset, join_op.right)

  return JoinSchema(left,right)



def schema_from_alias_op(alias_op, dataset):
  schema = interpret(dataset, alias_op.relation)
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

op_type_to_schemas = {
  LoadOp: schema_from_load,
  ProjectionOp: schema_from_projection_op,
  AliasOp: schema_from_alias_op,
  JoinOp: schema_from_join_op
}