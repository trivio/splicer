# test_operations.py
from nose.tools import *

from splicer import DataSet, Schema
from splicer.ast import *
from splicer.operations import walk

from .fixtures.employee_adapter import EmployeeAdapter


def test_walk():
    op = ProjectionOp(LoadOp("employees"), Var("full_name"))

    eq_(walk(op, lambda node: node), op)
