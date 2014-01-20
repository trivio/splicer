# test_operations.py
from nose.tools import *

from splicer import DataSet, Relation, Schema
from splicer.operations import walk
from splicer.ast import *

from .fixtures.employee_adapter import EmployeeAdapter


def test_walk():
  op = ProjectionOp(LoadOp('employees'), Var('full_name'))

  eq_(
    walk(op, lambda node: node),
    op
  )

