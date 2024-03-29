# test_schema_interpreter.py

from splicer.ast import *
from splicer.operations import query_zipper, visit_with, walk  # type: ignore
from splicer.schema_interpreter import resolve_schema  # type: ignore

from .fixtures import mock_data_set


def test_no_operations():
    """
    Without any operations the schema should be equal to the given
    relation.
    """

    dataset = mock_data_set()
    employees = dataset.get_relation("employees")

    schema = resolve_schema(dataset, LoadOp("employees")).schema

    assert schema.fields == employees.schema.fields


def test_table_function():

    dataset = mock_data_set()

    schema = resolve_schema(
        dataset, Function("flatten", LoadOp("employees"), StringConst("roles"))
    ).schema

    assert schema["roles"].type == "STRING"
    assert schema["roles"].mode == "NULLABLE"


# tests for Op's that overide their  new methods
def test_slice_op():
    dataset = mock_data_set()
    dataset.get_relation("employees")

    op = resolve_schema(dataset, SliceOp(LoadOp("employees"), 1))
    schema = op.schema

    assert schema == dataset.get_schema("employees")


def test_order_by_op():
    dataset = mock_data_set()
    dataset.get_relation("employees")

    op = resolve_schema(dataset, OrderByOp(LoadOp("employees"), "manager_id"))
    schema = op.schema

    assert schema == dataset.get_schema("employees")
