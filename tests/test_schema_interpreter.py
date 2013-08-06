# test_schema_interpreter.py

from nose.tools import *

from splicer import schema_interpreter
from splicer.ast import LoadOp
from .fixtures import mock_data_set


def test_no_operations():
  """
  Without any operations the schema should be equal to the given
  relation.
  """

  dataset   = mock_data_set()
  employees = dataset.get_relation('employees')
  schema    = schema_interpreter.interpret(dataset, LoadOp('employees'))

  assert_sequence_equal(
    schema.fields,
    employees.schema.fields
  )

