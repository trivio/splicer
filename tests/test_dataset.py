from nose.tools import *

from splicer import DataSet, Table, Query
from splicer.query_builder import QueryBuilder

from splicer.ast import LoadOp, ProjectionOp, Var

from .fixtures.mock_adapter import MockAdapter



def test_get_relation():
  dataset = DataSet()

  adapter = MockAdapter()
  dataset.add_adapter(adapter)

  s_table = adapter.get_relation('bogus')

  table = dataset.get_relation('bogus')
  eq_(table, s_table)

  assert_sequence_equal(
    dataset.relations, 
    [('bogus', s_table)]
  )

def test_query_builder():
  dataset = DataSet()
  adapter = MockAdapter()
  dataset.add_adapter(adapter)
  query = dataset.select('x')

  eq_(isinstance(query, QueryBuilder), True)
  eq_(query.dataset, dataset)
  eq_(query.column_exps, 'x')

def test_complier():
  adapter = MockAdapter()

  def compile(query):
    return lambda ctx, *params: Table(
      adapter,
      'results!', 
      schema = dict(
        fields = [
          dict(name="?column?", type="INTEGER")
        ]
      )
    )


  dataset = DataSet()
  dataset.add_adapter(adapter)
  dataset.set_compiler(compile)

  query = dataset.frm('bogus').query

  table = dataset.execute(query)

def test_query():
  dataset = DataSet()
  dataset.query('select 1').execute()


def test_views():
  dataset = DataSet()
  dataset.add_adapter(MockAdapter())


  # create a view off of an existing table
  dataset.select('x').frm('bogus').create_view('only_x')

  view = dataset.get_view('only_x')

  eq_(
    view,
    ProjectionOp(LoadOp('bogus'), Var('x'))
  )

  # create a view off of a view
  dataset.select('x').frm('only_x').create_view('only_x_from_x')

  view = dataset.get_view('only_x_from_x')

  eq_(
    view,
    # Todo: Implement a query optimizer that eliminates
    # redunant projections ops like the one we see below
    ProjectionOp(
      ProjectionOp(LoadOp('bogus'), Var('x')),
      Var('x')
    )
  )



