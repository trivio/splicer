# test_operations.py
from nose.tools import *

from splicer import DataSet, Relation, Schema
from splicer.operations import walk, replace_views
from splicer.ast import *

from .fixtures.employee_adapter import EmployeeAdapter


def test_walk():
  op = ProjectionOp(LoadOp('employees'), Var('full_name'))

  eq_(
    walk(op, lambda node: node),
    op
  )

def test_relpace_views():
  dataset = DataSet()
  dataset.add_adapter(EmployeeAdapter())

  no_managers = SelectionOp(
    LoadOp('employees'),
    IsOp(Var('manager_id'), NullConst())
  )

  dataset.create_view(
    'no_managers',
    no_managers
  )

  eq_(
    replace_views(LoadOp('no_managers'), dataset),
    no_managers
  )

  eq_(
    replace_views(
      JoinOp(
        LoadOp('no_managers'),
        LoadOp('no_managers')
      ),
      dataset
    ),

    JoinOp(
      no_managers,
      no_managers
    )

  )

