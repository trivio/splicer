from nose.tools import *

from splicer import DataSet, Table, Query
from splicer.dataset import replace_views
from splicer.query_builder import QueryBuilder

from splicer.schema import Schema
from splicer.ast import *
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


def test_get_schema():
  class Adapter(object):
    def has(self, name): return name == 'computed'

    def schema(self, name):
      return Function('myschema')

  dataset = DataSet()
  dataset.add_adapter(Adapter())

  # Todo: figure out why I have to invoke this decorator here
  @dataset.function()
  def myschema():
    return Schema([dict(name='field', type='string')])

  schema = dataset.get_schema('computed')

  eq_(
    schema,
    Schema([dict(name='field', type='string')])
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


def test_relpace_views():
  dataset = DataSet()
  dataset.add_adapter(MockAdapter())

  no_managers = SelectionOp(
    LoadOp('bogus'),
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

def test_relpace_view_within_a_view():
  dataset = DataSet()
  dataset.add_adapter(MockAdapter())

  dataset.create_view(
    'view1',
    LoadOp('bogus')
  )

  dataset.create_view(
    'view2',
    LoadOp('view1')
  )

  dataset.create_view(
    'view3',
    SelectionOp(LoadOp('view2'), IsOp(Var('x'), NullConst()))
  )

  eq_(
    replace_views(
      LoadOp('view3'), 
      dataset
    ),
    SelectionOp(LoadOp('bogus'), IsOp(Var('x'), NullConst()))
    
  )


