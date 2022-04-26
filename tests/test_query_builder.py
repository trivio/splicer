from splicer import Field, Query, Schema
from splicer.ast import *
from splicer.query_builder import QueryBuilder  # type: ignore

from . import assert_is_instance, compare
from .fixtures import mock_data_set


def test_execute():
    dataset = mock_data_set()
    qb = QueryBuilder(dataset).frm("employees")
    assert list(qb.execute()) == list(dataset.frm("employees").execute())


def test_from_bogus():
    dataset = mock_data_set()
    qb = QueryBuilder(dataset)

    qb_w_from = qb.frm("bogus")
    # ensure we maintain immutability by only returning
    # nev versions
    assert qb != qb_w_from

    q = qb_w_from.query
    assert_is_instance(q, Query)

    assert q.schema == dataset.get_schema("bogus")

    compare(q.operations, LoadOp("bogus"))


def test_select():
    dataset = mock_data_set()

    qb = QueryBuilder(dataset)
    assert qb.column_exps == "*"
    qb_w_select = qb.select("x,y")

    assert qb != qb_w_select
    assert qb_w_select.column_exps == "x,y"

    qb_w_select_and_from = qb_w_select.frm("bogus")

    q = qb_w_select_and_from.query

    assert_is_instance(q, Query)

    assert q.schema.fields == [
        Field(name="x", type="INTEGER", schema_name="bogus"),
        Field(name="y", type="INTEGER", schema_name="bogus"),
    ]

    compare(q.operations, ProjectionOp(LoadOp("bogus"), Var("x"), Var("y")))

    qb_select_y_from_bogus = qb.select("y").frm("bogus")
    assert qb_select_y_from_bogus.column_exps == "y"

    assert qb_select_y_from_bogus.query.schema.fields == [
        Field(name="y", type="INTEGER", schema_name="bogus")
    ]

    compare(
        qb_select_y_from_bogus.query.operations, ProjectionOp(LoadOp("bogus"), Var("y"))
    )


def test_where():
    dataset = mock_data_set()
    qb = QueryBuilder(dataset).frm("employees").where("employee_id = 123")

    assert qb.query.operations == SelectionOp(
        LoadOp("employees"), EqOp(Var("employee_id"), NumberConst(123))
    )


def test_projection_and_selection():
    dataset = mock_data_set()

    qb = (
        QueryBuilder(dataset)
        .select("full_name")
        .frm("employees")
        .where("employee_id = 123")
    )

    query = qb.query
    assert query.operations == ProjectionOp(
        SelectionOp(LoadOp("employees"), EqOp(Var("employee_id"), NumberConst(123))),
        Var("full_name"),
    )

    assert query.schema.fields == [
        Field(name="full_name", type="STRING", schema_name="employees")
    ]


def test_order_by():
    dataset = mock_data_set()
    qb = QueryBuilder(dataset).frm("employees").order_by("employee_id")

    assert qb.query.operations == OrderByOp(LoadOp("employees"), Var("employee_id"))


def test_order_by_multiple():
    dataset = mock_data_set()
    qb = (
        QueryBuilder(dataset)
        .frm("employees")
        .order_by("employee_id, full_name Desc, 123")
    )
    assert qb.query.operations == OrderByOp(
        LoadOp("employees"),
        Var("employee_id"),
        Desc(Var("full_name")),
        NumberConst(123),
    )


def test_group_by():
    dataset = mock_data_set()

    qb = (
        QueryBuilder(dataset)
        .select("manager_id, count()")
        .frm("employees")
        .group_by("manager_id")
    )

    assert qb.query.operations == GroupByOp(
        ProjectionOp(LoadOp("employees"), Var("manager_id"), Function("count")),
        Var("manager_id"),
    )


def test_all_aggregates():
    """Aggregation is possible if all the selected columns are aggregate functions"""

    dataset = mock_data_set()

    qb = QueryBuilder(dataset).select("count()").frm("employees")

    assert qb.query.operations == GroupByOp(
        ProjectionOp(LoadOp("employees"), Function("count"))
    )


def test_all_count_aliased():
    """Aggregation is possible if all the selected columns are aggregate functions"""

    dataset = mock_data_set()

    qb = QueryBuilder(dataset).select("count() as total").frm("employees")

    assert qb.query.operations == GroupByOp(
        ProjectionOp(LoadOp("employees"), RenameOp("total", Function("count")))
    )


def test_limit():

    dataset = mock_data_set()

    qb = QueryBuilder(dataset).frm("employees").limit(1)

    assert qb.query.operations == SliceOp(LoadOp("employees"), None, 1)


def test_offset():

    dataset = mock_data_set()

    qb = QueryBuilder(dataset).frm("employees").offset(1)

    assert qb.query.operations == SliceOp(LoadOp("employees"), 1, None)


def test_offset_and_limit():

    dataset = mock_data_set()

    qb = QueryBuilder(dataset).frm("employees").offset(1).limit(1)

    assert qb.query.operations == SliceOp(LoadOp("employees"), 1, 2)


def test_join():

    dataset = mock_data_set()

    query = (
        QueryBuilder(dataset)
        .select("employee.*, manager.full_name as manager")
        .frm("employees as employee")
        .join("employees as manager", on="manager.employee_id = employee.manager_id")
        .query
    )

    operations = ProjectionOp(
        JoinOp(
            AliasOp("employee", LoadOp("employees")),
            AliasOp("manager", LoadOp("employees")),
            EqOp(Var("manager.employee_id"), Var("employee.manager_id")),
        ),
        SelectAllExpr("employee"),
        RenameOp("manager", Var("manager.full_name")),
    )

    assert query.operations == operations


def test_join_subselect():
    dataset = mock_data_set()
    managers = (
        QueryBuilder(dataset)
        .select("employee_id as id, full_name as manager")
        .frm("employees as manager")
    )

    query = (
        QueryBuilder(dataset)
        .select("employee.*,  manager")
        .frm("employees as employee")
        .join(managers, on="manager.id = employee.manager_id")
        .query
    )

    operations = ProjectionOp(
        JoinOp(
            AliasOp("employee", LoadOp("employees")),
            ProjectionOp(
                AliasOp("manager", LoadOp("employees")),
                RenameOp("id", Var("employee_id")),
                RenameOp("manager", Var("full_name")),
            ),
            EqOp(Var("manager.id"), Var("employee.manager_id")),
        ),
        SelectAllExpr("employee"),
        Var("manager"),
    )

    assert query.operations == operations
