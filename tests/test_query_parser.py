from nose.tools import *
from splicer import query_parser

from splicer.ast import (
  NumberConst, StringConst, Var, Function, Tuple,
  NegOp, NotOp, MulOp, DivOp, ItemGetterOp, ParamGetterOp,
  AddOp, SubOp, 
  And, Or,

  ProjectionOp, SelectionOp, RenameOp, SelectAllExpr,
  GroupByOp
)

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
  ast = query_parser.parse_select('x, x as x2, 49929')
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
  ast = query_parser.parse_select('*')
  eq_(ast, ProjectionOp(SelectAllExpr()))

def test_parse_select_all_frm_table():
  ast = query_parser.parse_select('table.*, x')
  eq_(ast, ProjectionOp(SelectAllExpr('table'), Var('x')))


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




