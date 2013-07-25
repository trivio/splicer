from datetime import date

from nose.tools import *

from splicer import DataSet, Table, Query
from splicer.ast import *
from splicer.compilers.local import compile

from .fixtures.employee_server import EmployeeServer

def test_projection():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())



  q = Query(
    dataset, 
    'employees', 
    [ProjectionOp(Var('full_name'))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [('Tom Tompson',), ('Sally Sanders',), ('Mark Markty',)]
  )

def test_selection():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset, 
    'employees', 
    [SelectionOp(
      EqOp(Var('manager_id'), NullConst())
    )]
  )
  
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
    ]
  )


  q = Query(
    dataset, 
    'employees', 
    [SelectionOp(
      NotOp(EqOp(Var('manager_id'), NullConst()))
    )]
  )
  
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234)
    ]
  )

def test_addition():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())


  q = Query(
    dataset, 
    'employees', 
    [ProjectionOp(AddOp(Var('employee_id'), NumberConst(1)))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [(1235,), (4568,), (8902,)]
  )

def test_order_by():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())


  q = Query(
    dataset, 
    'employees', 
    [OrderByOp(Var('full_name'))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (8901, 'Mark Markty', date(2010, 3, 1), 1234),
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
    ]
  )

def test_order_by_asc():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())


  q = Query(
    dataset, 
    'employees', 
    [OrderByOp(Asc(Var('employee_id')))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234),
    ]
  )
