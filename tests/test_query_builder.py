from unittest import TestCase
from nose.tools import *

from insitu.query_builder import  QueryBuilder

from fixtures import mock_data_set


def test_from():
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

  q.columns = ["all the columns in bogus"]
  q.execute = "iterator of all the records"



  #q_final = q_w_from.validate()


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
  query =  qb_w_select_and_from.query

  assert_is_instance(q, Query)

  assert_sequence_equal(
    q.columns, 
    (
      Field(name="x", type="INTEGER")
      Field(name="y", type="INTEGER")
    )
  )

  assert_sequence_qual(
    list(q.execute()),
    ... data in the mock server ..

  )



def test_where():
  pass

