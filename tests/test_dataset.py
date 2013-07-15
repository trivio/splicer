from unittest import TestCase
from nose.tools import eq_

from insitu import DataSet, Table, Query
from insitu.query_builder import QueryBuilder
from fixtures.mock_server import MockServer



class TestDataSet(TestCase):

  def test_get_relation(self):
    dataset = DataSet()

    server = MockServer()
    dataset.add_server(server)

    s_table = server.get_table('bogus')

    table = dataset.get_relation('bogus')
    eq_(table, s_table)

    self.assertSequenceEqual(dataset.relations, [('bogus', s_table)])

  def test_query(self):
    dataset = DataSet()
    server = MockServer()
    dataset.add_server(server)
    query = dataset.select('x')
    
    eq_(isinstance(query, QueryBuilder), True)
    eq_(query.dataset, dataset)
    eq_(query.column_exps, 'x')


