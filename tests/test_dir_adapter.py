import os
import tempfile
import shutil

from nose.tools import *


from splicer.ast import *
from splicer.operations import query_zipper
from splicer.compilers.local import compile
from splicer.adapters.dir_adapter import DirAdapter


def setup_func():
  global path
  path = tempfile.mkdtemp()


def teardown_func():
  global path
  try:
    shutil.rmtree(path)
  finally:
    path =None


@with_setup(setup_func, teardown_func)
def test_evaluate():
  
  adapter = DirAdapter(
    songs = dict(
      root_dir = path,
      pattern = "{artist}/{album}/{track}.{ext}",
      filename_column="path",
    )
  )
  relation = adapter.get_relation('songs')

  op = LoadOp('songs')
  loc = query_zipper(op).leftmost_descendant()
  
  res = adapter.evaluate(loc)

  eq_(
    res.root(),
    Function(
      'extract_path',
      Function('files', Const(relation.root_dir)),
      Const(path + "/{artist}/{album}/{track}.{ext}")
    )
  )


def test_query_field_in_payload():
  """
  Querying a field inside the payload should result
  in the LoadOp being rewritten as

  SelectionOp(Function('decode', Function('extract_path', Function('files'))))
  """

  adapter = DirAdapter(
    employees = dict(
      root_dir = "/",
      pattern = "{department}",
      filename_column="path",
      decode = "auto",
      schema = dict(fields=[
        dict(type='STRING', name='department'),
        dict(type='INTEGER', name='id'),
        dict(type='STRING', name='full_name'),
        dict(type='INTEGER', name='salary'),
        dict(type='INTEGER', name='manager_id'),
      ])
    )
  )


  op = SelectionOp(LoadOp('employees'), GeOp(Var('salary'), Const(40000)))

  loc = query_zipper(op).leftmost_descendant()
  
  res = adapter.evaluate(loc)
  relation = adapter.get_relation('employees')


 
  eq_(
    res.root(),
    SelectionOp(
      Function(
        'decode',
        Function(
          'extract_path',
          Function('files', Const(relation.root_dir)),
          Const(relation.root_dir + "{department}")
        ),
        Const('auto')
      ),
      GeOp(Var('salary'), Const(40000))
    )
  )

def test_query_field_from_path():
  """
  Queries with SelectionOps that reference only fields
  parsed from the directory structre will rewrite
  the query so that the file list is filtered before 
  opening/decoding the files.
  """

  adapter = DirAdapter(
    employees = dict(
      root_dir = "/",
      pattern = "{department}",
      filename_column="path",
      decode = "auto",
      schema = dict(fields=[
        dict(type='STRING', name='department'),
        dict(type='INTEGER', name='id'),
        dict(type='STRING', name='full_name'),
        dict(type='INTEGER', name='salary'),
        dict(type='INTEGER', name='manager_id'),
      ])
    )
  )


  op = SelectionOp(LoadOp('employees'), EqOp(Var('department'), Const('sales')))

  loc = query_zipper(op).leftmost_descendant()
  
  res = adapter.evaluate(loc)
  relation = adapter.get_relation('employees')

  
 
  eq_(
    res.root(),
    Function(
      'decode',
      SelectionOp(
        Function(
          'extract_path',
          Function('files', Const(relation.root_dir)),
          Const(relation.root_dir + "{department}")
        ),
        EqOp(Var('department'), Const('sales'))
      ),
      Const('auto')
    )
  )


def test_query_field_from_path_and_contents():
  """
  Queries with SelectionOps that reference both  fields
  parsed from the directory structre and content will 
  rewrite the query so that the file list is filtered before 
  opening/decoding the files and finally filtered by the field
  from the content
  """

  adapter = DirAdapter(
    employees = dict(
      root_dir = "/",
      pattern = "{department}",
      filename_column="path",
      decode = "auto",
      schema = dict(fields=[
        dict(type='STRING', name='department'),
        dict(type='INTEGER', name='id'),
        dict(type='STRING', name='full_name'),
        dict(type='INTEGER', name='salary'),
        dict(type='INTEGER', name='manager_id'),
      ])
    )
  )


  op = SelectionOp(
    LoadOp('employees'),
    And(
      EqOp(Var('department'), Const('sales')),
      GeOp(Var('salary'), Const(40000)),
    )
  )

  loc = query_zipper(op).leftmost_descendant()
  
  res = adapter.evaluate(loc)
  relation = adapter.get_relation('employees')

  
 
  eq_(
    res.root(),
    SelectionOp(  
      Function(
        'decode',
        SelectionOp(
          Function(
            'extract_path',
            Function('files', Const(relation.root_dir)),
            Const(relation.root_dir + "{department}")
          ),
          EqOp(Var('department'), Const('sales'))
        ),
        Const('auto')
      ),
      GeOp(Var('salary'), Const(40000))
    )
  )
