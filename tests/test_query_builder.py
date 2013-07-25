from nose.tools import *

from splicer import Query, Schema, Field
from splicer.query_builder import  QueryBuilder
from splicer.ast import ProjectionOp, SelectionOp, Var, EqOp, NumberConst, OrderByOp, Desc

from .fixtures import mock_data_set


def test_from_bogus():
  dataset = mock_data_set()
  qb = QueryBuilder(dataset)

  qb_w_from = qb.frm('bogus')
  # ensure we maintain immutability by only returning
  # nev versions
  assert_is_not(qb, qb_w_from)


  eq_(qb_w_from.relation_name, 'bogus')

  q  = qb_w_from.query
  assert_is_instance(q, Query)

  assert_equal(
    q.schema,
    dataset.get_schema('bogus')
  )

  assert_equal(
    q.operations,
    []
  )


def test_select():
  dataset = mock_data_set()

  qb = QueryBuilder(dataset)
  eq_(qb.column_exps, '*')
  qb_w_select = qb.select('x,y')

  assert_is_not(qb, qb_w_select)
  eq_(qb_w_select.column_exps, 'x,y')

  # selecting w/o specifying relations raises a ValueError
  assert_raises(ValueError, lambda : qb_w_select.query)

  qb_w_select_and_from = qb_w_select.frm('bogus')

  q =  qb_w_select_and_from.query

  assert_is_instance(q, Query)

  assert_sequence_equal(
    q.schema.fields, 
    [
      Field(name="x", type="INTEGER"),
      Field(name="y", type="INTEGER")
    ]
  )

  assert_equal(
    q.operations,
    [ProjectionOp(Var('x'), Var('y'))]
  )

  qb_select_y_from_bogus = qb.select('y').frm('bogus')
  eq_(qb_select_y_from_bogus.column_exps, 'y')

  assert_sequence_equal(
    qb_select_y_from_bogus.query.schema.fields, 
    [
      Field(name="y", type="INTEGER")
    ]
  )

  assert_equal(
    qb_select_y_from_bogus.query.operations,
    [ProjectionOp(Var('y'))]
  )


def test_where():
  dataset = mock_data_set()
  qb = QueryBuilder(dataset).frm('employees').where('employee_id = 123')

  assert_equal(
    qb.query.operations,
    [SelectionOp(EqOp(Var('employee_id'), NumberConst(123)))]
  )

def test_projection_and_selection():
  dataset = mock_data_set()

  qb = QueryBuilder(dataset).select(
    'full_name'
  ).frm('employees').where('employee_id = 123')

  query = qb.query
  assert_equal(
    query.operations,
    [
      SelectionOp(EqOp(Var('employee_id'), NumberConst(123))),
      ProjectionOp(Var('full_name'))
    ]
  )

  assert_sequence_equal(
    query.schema.fields, 
    [
      Field(name="full_name", type="STRING")
    ]
  )


def test_order_by():
  dataset = mock_data_set()
  qb = QueryBuilder(dataset).frm('employees').order_by('employee_id')

  assert_equal(
    qb.query.operations,
    [OrderByOp(Var('employee_id'))]
  )

def test_order_by_multiple():
  dataset = mock_data_set()
  qb = QueryBuilder(dataset).frm('employees').order_by('employee_id, full_name Desc, 123')

  assert_equal(
    qb.query.operations,
    [OrderByOp(Var('employee_id'), Desc(Var('full_name')), NumberConst(123))]
  )


