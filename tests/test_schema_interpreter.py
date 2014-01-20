# test_schema_interpreter.py

from nose.tools import *
from functools import partial
from splicer.schema_interpreter import resolve_schema

from splicer.ast import LoadOp, StringConst, Function
from splicer.operations import query_zipper, walk, visit_with
from .fixtures import mock_data_set


def test_no_operations():
  """
  Without any operations the schema should be equal to the given
  relation.
  """

  dataset   = mock_data_set()
  employees = dataset.get_relation('employees')
  loc = query_zipper(LoadOp('employees'))
  schema = resolve_schema(dataset, loc, loc.node()).node().schema

  assert_sequence_equal(
    schema.fields,
    employees.schema.fields
  )

def test_table_function():
  """
  """

  dataset   = mock_data_set()
  loc = query_zipper(
    Function('flatten', LoadOp('employees'), StringConst('roles'))
  )

  schema = walk(
    Function('flatten', LoadOp('employees'), StringConst('roles')),
    visit_with(
      dataset,
      (lambda loc: True, resolve_schema)
    )
  ).schema

  eq_(schema['roles'].type,'STRING')
  eq_(schema['roles'].mode,'NULLABLE')



