# test_operations.py
from splicer import DataSet, Schema
from splicer.ast import *
from splicer.operations import walk  # type: ignore

from .fixtures.employee_adapter import EmployeeAdapter


def test_walk():
    op = ProjectionOp(LoadOp("employees"), Var("full_name"))

    assert walk(op, lambda node: node) == op
