from datetime import date
from nose.tools import *

from splicer import Query, Schema, Field
from splicer.adapters.dir_adapter import DirAdapter

import os
import tempfile
import shutil

def setup_func():
  global path
  path = tempfile.mkdtemp()


def teardown_func():
  global path
  try:
    shutil.rmtree(path)
  finally:
    path =None


from splicer.ast import *
from splicer.operations import query_zipper
from splicer.compilers.local import compile
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

