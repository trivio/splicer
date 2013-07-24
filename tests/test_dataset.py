from nose.tools import *

from splicer import DataSet, Table, Query
from splicer.query_builder import QueryBuilder
from .fixtures.mock_server import MockServer



def test_get_relation():
  dataset = DataSet()

  server = MockServer()
  dataset.add_server(server)

  s_table = server.get_table('bogus')

  table = dataset.get_relation('bogus')
  eq_(table, s_table)

  assert_sequence_equal(
    dataset.relations, 
    [('bogus', s_table)]
  )

def test_query_builder():
  dataset = DataSet()
  server = MockServer()
  dataset.add_server(server)
  query = dataset.select('x')

  eq_(isinstance(query, QueryBuilder), True)
  eq_(query.dataset, dataset)
  eq_(query.column_exps, 'x')

def test_complier():
  def compile(query):
    return lambda ctx, *params: Table(
      'results!', 
      schema = dict(
        fields = [
          dict(name="?column?", type="INTEGER")
        ]
      )
    )


  dataset = DataSet()
  server = MockServer()
  dataset.add_server(server)
  dataset.set_compiler(compile)

  query = dataset.frm('bogus').query

  table = dataset.execute(query)
