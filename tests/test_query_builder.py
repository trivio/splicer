from nose.tools import *

from insitu import Query, Schema, Field
from insitu.query_builder import  QueryBuilder

from .fixtures import mock_data_set


def test_from_bogus():
  dataset = mock_data_set()
  qb = QueryBuilder(dataset)

  qb_w_from = qb.frm('bogus')
  # ensure we maintain immutability by only returning
  # nev versions
  assert_is_not(qb, qb_w_from)

  relations = [r.name for r in qb_w_from.relations]
  assert_sequence_equal(relations, ('bogus',))

  q  = qb_w_from.query
  assert_is_instance(q, Query)

  assert_equal(
    q.schema,
    dataset.get_relation('bogus').schema
  )

  #q.execute = "iterator of all the records"
  assert_sequence_equal(
    list(q.execute()),
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
  
  assert_sequence_equal(
    list(q.execute()),
    []
  )


  qb_select_y_from_bogus = qb.select('y').frm('bogus')
  eq_(qb_select_y_from_bogus.column_exps, 'y')

  assert_sequence_equal(
    qb_select_y_from_bogus.query.schema.fields, 
    [
      Field(name="y", type="INTEGER")
    ]
  )




def test_where():
  pass

