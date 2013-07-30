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
    [ LoadOp('employees'), ProjectionOp(Var('full_name')) ]
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
    [
      LoadOp('employees'), 
      SelectionOp(
        EqOp(Var('manager_id'), NullConst())
      )
    ]
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
    [
      LoadOp('employees'),
      SelectionOp(
        NotOp(EqOp(Var('manager_id'), NullConst()))
      )
    ]
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
    [LoadOp('employees'), ProjectionOp(AddOp(Var('employee_id'), NumberConst(1)))]
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
    [LoadOp('employees'), OrderByOp(Var('full_name'))]
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
    [LoadOp('employees'), OrderByOp(Asc(Var('employee_id')))]
  )
  evaluate = compile(q)

  assert_sequence_equal(list(evaluate(dict(dataset=dataset)))
    ,
    [
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234),
    ]
  )

def test_function_calls():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  dataset.add_function(
    name = 'initials', 
    function = lambda name: ''.join([p[0] for p in name.split()]) if name else None,
    returns = dict(name="initials", type="STRING")
  )


  q = Query(
    dataset, 
    [LoadOp('employees'), ProjectionOp(Function('initials', Var('full_name')))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      ('TT',),
      ('SS',),
      ('MM',),
    ]
  )


def test_decorator_function_calls():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  @dataset.function(returns=dict(name="initials", type="STRING"))
  def initials(name):
    if name:
      return ''.join([p[0] for p in name.split()])
    else:
      return None

 

  q = Query(
    dataset,  
    [LoadOp('employees'), ProjectionOp(Function('initials', Var('full_name')))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      ('TT',),
      ('SS',),
      ('MM',),
    ]
  )

def test_aggregation_whole_table():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset,  
    [LoadOp('employees'), GroupByOp(ProjectionOp(Function('count')))]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (3,),
    ]
  )


def test_aggregation_on_column():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset, 
    [
      LoadOp('employees'),
      GroupByOp(
        ProjectionOp(Var('manager_id'), Function('count')), 
        Var('manager_id')
      )
    ]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (None,1),
      (1234,2)
    ]
  )

def test_limit():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset, 
    [LoadOp('employees'), SliceOp(1)]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (1234, 'Tom Tompson', date(2009, 1, 17), None),
    ]
  )

def test_offset():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset, 
    [LoadOp('employees'), SliceOp(1,None)]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234),
 
    ]
  )

def test_offset_and_limit():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset, 
    [LoadOp('employees'), SliceOp(1,2)]
  )
  evaluate = compile(q)

  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234),
    ]
  )


def test_self_join():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())


  q = Query(
    dataset,  
    [
      JoinOp(
        AliasOp('manager', LoadOp('employees')),
        AliasOp('employee', LoadOp('employees')),
        EqOp(Var('manager.employee_id'), Var('employee.manager_id'))
      )
    ]
  )
  evaluate = compile(q)



  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234, 1234, 'Tom Tompson', date(2009, 1, 17), None),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234, 1234, 'Tom Tompson', date(2009, 1, 17), None)
    ]
  )

def test_self_join_with_projection():
  dataset = DataSet()
  dataset.add_server(EmployeeServer())

  q = Query(
    dataset,  
    [
      JoinOp(
        AliasOp('manager', LoadOp('employees')),
        AliasOp('employee', LoadOp('employees')),
        EqOp(Var('manager.employee_id'), Var('employee.manager_id'))
      ),
      ProjectionOp(
        SelectAllExpr('employee'),
        RenameOp('manager', Var('manager.full_name'))
      )
    ]
  )

  evaluate = compile(q)



  assert_sequence_equal(
    list(evaluate(dict(dataset=dataset))),
    [
      (4567, 'Sally Sanders', date(2010, 2, 24), 1234, 'Tom Tompson'),
      (8901, 'Mark Markty', date(2010, 3, 1), 1234,  'Tom Tompson')
    ]
  )
