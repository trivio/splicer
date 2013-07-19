from nose.tools import *

from insitu import Schema
from .fixtures import mock_data_set


def __test_projection():
  employees = mock_data_set().get_relation('employees')
  op = relational_ops.ProjectOp(
    Schema([dict(
      name="employee_id",
      type="INTEGER"
    )]),
    lambda row, ctx: row['employee_id']
  )


  rows = employees.rows(None, None)

  assert_sequence_equal(
    list(op(rows, None)),
    [(1234,), (4567,), (8901,)]
  )

def __test_selection():
  employees = mock_data_set().get_relation('employees')
  op = relational_ops.SelectionOp(employees.schema)

  assert_sequence_equal(
    list(op(employees, None)),
    list(employees.rows(None, None))
  )
  