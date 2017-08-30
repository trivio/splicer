from nose.tools import *
from . import compare

from splicer import query_parser

from splicer.ast import *

def test_cast_op():
  statement = "CAST(column AS BIGINT)"
  ast = query_parser.parse(statement)

  assert_is_instance(ast, CastOp)
  assert_is_instance(ast.expr, Var)
  eq_(ast.expr.path, 'column')
  eq_(ast.type, 'BIGINT')



def test_single_case_when_1():
  statement = "CASE WHEN column = '' THEN column ELSE CONCAT('CMC', column) END"

  ast = query_parser.parse(statement)

  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Function)
  assert_is_instance(ast.conditions[0]['condition'], EqOp)
  assert_is_instance(ast.conditions[0]['expr'], Var)
  eq_(ast.conditions[0]['condition'].lhs.path, 'column')
  eq_(ast.conditions[0]['condition'].rhs.const, '')
  eq_(ast.conditions[0]['expr'].path, 'column')
  eq_(ast.default_value.name, 'CONCAT')
  eq_(ast.default_value.args[0].const, 'CMC')
  eq_(ast.default_value.args[1].path, 'column')

def test_single_case_when_2():
  statement = "CASE WHEN column LIKE 'true' THEN 1 ELSE 0 END"

  ast = query_parser.parse(statement)
  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Const)
  assert_is_instance(ast.conditions[0]['condition'], LikeOp)
  assert_is_instance(ast.conditions[0]['expr'], Const)
  eq_(ast.default_value.const, 0)

def test_single_case_when_3():
  statement = "CASE WHEN column != '' THEN MD5(LOWER(column)) ELSE '' END"

  ast = query_parser.parse(statement)
  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Const)
  assert_is_instance(ast.conditions[0]['condition'], NeOp)
  assert_is_instance(ast.conditions[0]['expr'], Function)
  eq_(ast.conditions[0]['condition'].lhs.path, 'column')
  eq_(ast.conditions[0]['condition'].rhs.const, '')
  eq_(ast.conditions[0]['expr'].name, 'MD5')
  assert_is_instance(ast.conditions[0]['expr'].args[0], Function)
  eq_(ast.conditions[0]['expr'].args[0].name, 'LOWER')
  eq_(ast.conditions[0]['expr'].args[0].args[0].path, 'column')
  eq_(ast.default_value.const, '')

def test_single_case_when_4():
  statement = "CASE " \
              " WHEN column != '' " \
              " THEN REFLECT('org.apache.commons.codec.digest.DigestUtils', 'shaHex', LOWER(column)) " \
              " ELSE '' " \
              "END"

  ast = query_parser.parse(statement)
  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Const)
  assert_is_instance(ast.conditions[0]['condition'], NeOp)
  assert_is_instance(ast.conditions[0]['expr'], Function)
  eq_(ast.conditions[0]['condition'].lhs.path, 'column')
  eq_(ast.conditions[0]['condition'].rhs.const, '')
  eq_(ast.default_value.const, '')
  eq_(ast.conditions[0]['expr'].name, 'REFLECT')
  assert_is_instance(ast.conditions[0]['expr'].args[0], Const)
  assert_is_instance(ast.conditions[0]['expr'].args[1], Const)
  assert_is_instance(ast.conditions[0]['expr'].args[2], Function)
  eq_(ast.conditions[0]['expr'].args[0].const, 'org.apache.commons.codec.digest.DigestUtils')
  eq_(ast.conditions[0]['expr'].args[1].const, 'shaHex')
  eq_(ast.conditions[0]['expr'].args[2].name, 'LOWER')
  eq_(ast.conditions[0]['expr'].args[2].args[0].path, 'column')

def test_single_case_when_5():
  statement = "CASE " \
              " WHEN column RLIKE '^\\d\\d\\d\\d$' THEN column " \
              " ELSE '' " \
              "END"

  ast = query_parser.parse(statement)
  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Const)
  assert_is_instance(ast.conditions[0]['condition'], RLikeOp)
  eq_(ast.conditions[0]['condition'].lhs.path, 'column')
  eq_(ast.conditions[0]['condition'].rhs.const, '^\\d\\d\\d\\d$')
  eq_(ast.conditions[0]['expr'].path, 'column')
  eq_(ast.default_value.const, '')


def test_multiple_case_when():
  statement = "CASE " \
                " WHEN column = '' THEN column " \
                " WHEN column = 'a' THEN column_a " \
                " WHEN column = 'b' THEN column_b " \
                " ELSE CONCAT('CMC', column) " \
                "END"

  ast = query_parser.parse(statement)

  assert_is_instance(ast, CaseWhenOp)
  assert_is_instance(ast.default_value, Function)
  assert_is_instance(ast.conditions[0]['condition'], EqOp)
  assert_is_instance(ast.conditions[0]['expr'], Var)
  assert_is_instance(ast.conditions[1]['condition'], EqOp)
  assert_is_instance(ast.conditions[1]['expr'], Var)
  assert_is_instance(ast.conditions[2]['condition'], EqOp)
  assert_is_instance(ast.conditions[2]['expr'], Var)
  eq_(ast.conditions[0]['condition'].lhs.path, 'column')
  eq_(ast.conditions[0]['condition'].rhs.const, '')
  eq_(ast.conditions[1]['condition'].lhs.path, 'column')
  eq_(ast.conditions[1]['condition'].rhs.const, 'a')
  eq_(ast.conditions[2]['condition'].lhs.path, 'column')
  eq_(ast.conditions[2]['condition'].rhs.const, 'b')
  eq_(ast.conditions[0]['expr'].path, 'column')
  eq_(ast.conditions[1]['expr'].path, 'column_a')
  eq_(ast.conditions[2]['expr'].path, 'column_b')
  eq_(ast.default_value.name, 'CONCAT')
  eq_(ast.default_value.args[0].const, 'CMC')
  eq_(ast.default_value.args[1].path, 'column')



def test_more_case_when():
  statement = """CASE
  WHEN
      (LOWER(x) not in ('blah', 'foo', 'baz'))
      AND (y not like 'pattern%' OR LOWER(zz) != 'hoo ha')
  THEN 1
  ELSE 0
END"""
  ast = query_parser.parse(statement)
  assert_is_instance(ast, CaseWhenOp)

def test_parse_int():
  ast = query_parser.parse('123')
  assert_is_instance(ast, NumberConst)
  eq_(ast.const, 123)

def test_parse_neg_int():
  ast = query_parser.parse('-123')
  assert_is_instance(ast, NegOp)
  assert_is_instance(ast.expr, NumberConst)
  eq_(ast.expr.const, 123)

def test_parse_not_int():
  ast = query_parser.parse('not 1')
  assert_is_instance(ast, NotOp)
  assert_is_instance(ast.expr, NumberConst)
  eq_(ast.expr.const, 1)

def test_parse_positive_int():
  ast = query_parser.parse('+1')
  assert_is_instance(ast, NumberConst)
  eq_(ast.const, 1)


def test_parse_mul():
  ast = query_parser.parse('1 *2')
  assert_is_instance(ast, MulOp)

def test_parse_div():
  ast = query_parser.parse('1 / 2')
  assert_is_instance(ast, DivOp)  

def test_parse_add():
  ast = query_parser.parse('1  + 2')
  assert_is_instance(ast, AddOp)

def test_parse_string():
  ast = query_parser.parse('"Hi mom"')
  assert_is_instance(ast, StringConst)
  eq_(ast.const, "Hi mom")

def test_parse_variable():
  ast = query_parser.parse('x')
  assert_is_instance(ast, Var)
  eq_(ast.path, "x")

def test_parse_variable_path():
  ast = query_parser.parse('foo.x')
  assert_is_instance(ast, Var)
  eq_(ast.path, "foo.x")

def test_parse_incomplete_variable_path():
  assert_raises(SyntaxError, query_parser.parse, 'foo.')

def test_parse_tuple():
  ast = query_parser.parse('(1,2, "a")')
  assert_is_instance(ast, Tuple)
  eq_(len(ast.exprs), 3)
  assert_is_instance(ast.exprs[0], NumberConst)
  assert_is_instance(ast.exprs[1], NumberConst)
  assert_is_instance(ast.exprs[2], StringConst)

def test_parse_function_no_args():
  ast = query_parser.parse('foo()')
  assert_is_instance(ast, Function)
  eq_(ast.name, "foo")
  eq_(ast.args, ())



def test_parse_incomplete_function():
  assert_raises(SyntaxError, query_parser.parse, 'foo(')

def test_parse_function_with_args():
  ast = query_parser.parse('foo(1)')
  assert_is_instance(ast, Function)
  eq_(len(ast.args), 1)
  assert_is_instance(ast.args[0], NumberConst)
  eq_(ast.args[0].const, 1)

def test_parse_function_with_multiple_args():
  ast = query_parser.parse('foo(1, x, "hi")')
  assert_is_instance(ast, Function)
  eq_(len(ast.args), 3)
  assert_is_instance(ast.args[0], NumberConst)
  assert_is_instance(ast.args[1], Var)
  assert_is_instance(ast.args[2], StringConst)
  eq_(ast.args[0].const, 1)
  eq_(ast.args[1].path, 'x')
  eq_(ast.args[2].const, 'hi')


def test_parse_is():
  ast = query_parser.parse('x is y')
  eq_(
    ast,
    IsOp(Var('x'), Var('y'))
  )

  ast = query_parser.parse('x is not y')
  eq_(
    ast,
    IsNotOp(Var('x'), Var('y'))
  )

def test_parse_invalid_is():
  assert_raises(SyntaxError, query_parser.parse, 'is')

def test_parse_is_null():
  ast = query_parser.parse('x is null')
  eq_(
    ast,
    IsOp(Var('x'), NullConst())
  )

def test_between():
  ast = query_parser.parse('x  between 1 and 2')
  eq_(
    ast,
    BetweenOp(Var('x'),  NumberConst(1), NumberConst(2) )
  )


  ast = query_parser.parse("x  between '1' and '2'")

  eq_(
    ast,
    BetweenOp(Var('x'),  StringConst('1'), StringConst('2') )
  )

def test_in():
  ast = query_parser.parse('x in (1, 2)')

  eq_(
    ast,
    InOp(Var('x'),  Tuple(NumberConst(1), NumberConst(2) ))
  )

def test_not_in():
  ast = query_parser.parse('x not in (1, 2)')

  eq_(
    ast,
    NotOp(InOp(Var('x'),  Tuple(NumberConst(1), NumberConst(2))))
  )


def test_parse_itemgetter():
  ast = query_parser.parse('$0')
  assert_is_instance(ast, ItemGetterOp)
  eq_(ast.key, 0)

  ast = query_parser.parse('$blah')
  assert_is_instance(ast, ItemGetterOp)
  eq_(ast.key, 'blah')

def test_parse_paramgetter():
  ast = query_parser.parse('?0')
  assert_is_instance(ast, ParamGetterOp)
  eq_(ast.expr, 0)

def test_parse_select_core():

  ast = query_parser.parse_select(LoadOp('bogus'), 'x, x as x2, 49929')
  assert_is_instance(ast, ProjectionOp)

  assert_is_instance(ast.exprs[0], Var)
  eq_(ast.exprs[0].path, 'x')
  
  assert_is_instance(ast.exprs[1], RenameOp)
  eq_(ast.exprs[1].name, 'x2')
  assert_is_instance(ast.exprs[1].expr, Var)
  eq_(ast.exprs[1].expr.path, 'x')
  
  assert_is_instance(ast.exprs[2], NumberConst)
  eq_(ast.exprs[2].const, 49929)

def test_parse_select_all():
  ast = query_parser.parse_select(LoadOp('bogus'), '*')
  eq_(ast, LoadOp('bogus'))

def test_parse_select_all_frm_table():
  ast = query_parser.parse_select(LoadOp('table'), 'table.*, x')
  eq_(ast, ProjectionOp(LoadOp('table'), SelectAllExpr('table'), Var('x')))


def test_parse_and():
  ast = query_parser.parse('x = 1 and z=2')
  assert_is_instance(ast, And)

def test_parse_or():
  ast = query_parser.parse('x = 1 or z=2')
  assert_is_instance(ast, Or)

def test_group_by_core_expr():
  ast = query_parser.parse_group_by('x,y')
  eq_(
    ast,
    [Var('x'), Var('y')]
  )

def test_parse_statement():
  ast = query_parser.parse_statement('select 1')

  eq_(
    ast,
    ProjectionOp(LoadOp(''), NumberConst(1))
  )


  ast = query_parser.parse_statement('select 1 from employees')

  eq_(
    ast,
    ProjectionOp(LoadOp('employees'), NumberConst(1))
  )

  ast = query_parser.parse_statement('select full_name from employees')

  eq_(
    ast,
    ProjectionOp(LoadOp('employees'), Var('full_name'))
  )

  ast = query_parser.parse_statement('''
    select full_name from employees as employee
  ''')

  eq_(
    ast,
    ProjectionOp(
      AliasOp('employee',LoadOp('employees')), 
      Var('full_name')
    )
  )

  ast = query_parser.parse_statement('''
    select full_name 
    from employees as employee, employees as manager
  ''')


  eq_(
    ast,
    ProjectionOp(
      JoinOp(
        AliasOp('employee',LoadOp('employees')),
        AliasOp('manager',LoadOp('employees'))
      ), 
      Var('full_name')
    )
  )


  ast = query_parser.parse_statement('''
    select full_name 
    from employees
    where manager_id is not null
  ''')

  eq_(
    ast,
    ProjectionOp(
      SelectionOp(
        LoadOp('employees'),
        IsNotOp(Var('manager_id'), NullConst())
      ), 
      Var('full_name')
    )
  )

  ast = query_parser.parse_statement('''
    select full_name 
    from employees as employee, employees as managers on employee.manager_id = managers.employee_id

  ''')


  ast = query_parser.parse_statement('''
    select manager_id, count() from employees
  ''')

  ast = query_parser.parse_statement('''
    select manager_id, count() from 
    employees
    group by manager_id
  ''')

  ast = query_parser.parse_statement('''
    select manager_id, count() from 
    employees
    group by manager_id
    order by count
  ''')

  op = OrderByOp(
    GroupByOp(
      ProjectionOp(
        LoadOp('employees'),
        Var('manager_id'),
        Function('count')
      ),
      Var('manager_id')
    ),
    Var('count')
  )

  eq_(
    ast,
    op
  )

  ast = query_parser.parse_statement(''' 
    select count() from top_10, top_10
  ''')

  ast = query_parser.parse_statement(''' 
  select t1.* from top_10 as t1
  ''')

  ast = query_parser.parse_statement(''' 
  select manager_id, count() from docs group by manager_id order by count desc limit 10
  ''')


def test_table_functions():

  ast = query_parser.parse_statement(''' 
  select *
  from flatten(docs, 'scripts')
  ''')
  
  op = Function('flatten', LoadOp('docs'), StringConst('scripts'))

  eq_(ast,op)

  ast = query_parser.parse_statement(''' 
  select *
  from flatten(select * from docs, "scripts")
  ''')

  eq_(ast,op)


def test_union_all():
  ast = query_parser.parse_statement(''' 
  select field1, field2 from table1
  union all
  select field1, field2 from table2
  ''')


  compare(
    ast,
    UnionAllOp(
      ProjectionOp(
        LoadOp('table1'),
        Var('field1'),
        Var('field2')
      ),
      ProjectionOp(
        LoadOp('table2'),
        Var('field1'),
        Var('field2')
      )
    )
  )

