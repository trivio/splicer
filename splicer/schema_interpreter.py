# schema_interpreter.py
"""
Module used to interpret the AST into a schema based on a given relation.
"""

from .schema import Schema
from .field import Field
from .ast import ProjectionOp, SelectionOp, RenameOp, Var, Function, Const

def interpret(dataset, relation, operations):
  """
  Given an ast and a dataset return the schema that will result
  after all the operations of the AST are applied.
  """
  
  schema = relation.schema
  for operation in operations:
    op_type = type(operation)
    dispatch = op_type_to_schemas.get(
      op_type, 
      lambda operation, dataset, schema: schema
    )
    schema = dispatch(operation, dataset, schema)

  return schema

def schema_from_projection_op(projection_op, dataset, schema):
  """
  Given a projection_op, datset and existing schema, return the new
  schema.
  """
  fields = []
  for expr in projection_op.exprs:
    fields.append(field_from_expr(expr, dataset, schema))
  return Schema(fields)

def field_from_expr(expr, dataset, schema):
  """
  """
  expr_type = type(expr)
  if expr_type == Var:
    return field_from_var(expr, schema)
  elif issubclass(expr_type, ConstExpr):
    return field_from_const(expr)
  elif expr_type == FunctionExpr:
    return field_from_function(expr, dataset, schema)
  elif expr_type == RenameOp:
    return field_from_rename_op(expr, dataset, schema)


def field_from_var(var_expr, schema):
  return schema[var_expr.path]

def field_from_function(function_expr, dataset, schema):
  name = function_expr.name
  function = dataset.get_function(function_expr.name)
  return Field(name=name, type=function.return_type)

def field_from_rename_op(expr, dataset, schema):
  field = field_from_expr(expr.expr, dataset, schema)
  return field.new(name=expr.name)

op_type_to_schemas = {
  ProjectionOp: schema_from_projection_op
}