from sys import getsizeof

from nose.tools import *

from splicer import Relation, Schema
from splicer.compilers.join import (
  nested_block_join,
  buffered,
  record_size,
  join_keys,
  join_keys_expr,
  hash_join
)
from splicer.ast import EqOp, And, Var, NumberConst


SCHEMA_1 = Schema(name="t1", fields=[dict(name='x', type="INTEGER")])

def t1(ctx=None):
  return Relation(
    SCHEMA_1,
    iter((
      (1,),
      (2,)
    ))
  )

SCHEMA_2 = Schema(
  name="t2", 
  fields=[
    dict(name='y', type="INTEGER"),
    dict(name='z', type="INTEGER")
  ]
)

def t2(ctx=None): 
  return Relation(
    SCHEMA_2,
    iter((
      (1,0),
      (1,1),
      (3,1)
    ))
  )
 

def test_record_size():
  t = (1,2, "blah")
  eq_(
    record_size(t),
    getsizeof(t) + getsizeof(t[0]) + getsizeof(t[1]) + getsizeof(t[2])
  )

def test_buffering():
  t = (1,2, "blah")
  sz = record_size(t)

  l = (t,) * 10

  eq_(
    len(list(buffered(l, sz))),
    10
  )

  eq_(
    len(list(buffered(l, sz*2))),
    5
  )

  eq_(
    len(list(buffered(l, sz*10))),
    1
  )

def test_nested_block_join():
  r = (
    (1,),
    (2,),
    (3,),
  )

  s = (
    ('a',),
    ('b',),
    ('c',),
  )

  j = tuple(nested_block_join(
    lambda ctx: iter(r),
    lambda ctx: iter(s),
    lambda r,ctx: True, 
    {}
  ))

  assert_sequence_equal(
    j,
    (
      (1, 'a'),
      (2, 'a'),
      (3, 'a'),
      (1, 'b'),
      (2, 'b'),
      (3, 'b'),
      (1, 'c'),
      (2, 'c'),
      (3, 'c'),
    )
  )


def test_join_key_expr():

  simple_op = EqOp(Var('t1.x'), Var('t2.y'))
  ((left_key, right_key),) = join_keys_expr(SCHEMA_1, SCHEMA_2, simple_op)

  ctx = None
  eq_(
    left_key((1,), ctx),
    1
  )

  eq_(
    right_key((1,0), ctx),
    1
  )

  simple_op = EqOp(Var('t2.y'), Var('t1.x'))
  ((left_key, right_key),) = join_keys_expr(SCHEMA_1,SCHEMA_2, simple_op)

  ctx = None
  eq_(
    left_key((1,), ctx),
    1
  )

  eq_(
    right_key((1,0), ctx),
    1
  )

  simple_op = EqOp(Var('t1.x'), NumberConst(1))
  assert_raises(ValueError, join_keys_expr,SCHEMA_1,SCHEMA_2, simple_op)



def test_join_keys():
  
  simple_op = EqOp(Var('t1.x'), Var('t2.y'))

  left_key, right_key = join_keys(SCHEMA_1,SCHEMA_2, simple_op)

  ctx = None
  eq_(
    left_key((1,), ctx),
    (1,)
  )

  eq_(
    right_key((1,0), ctx),
    (1,)
  )

  multi_key = And(
    EqOp(Var('t1.x'), Var('t2.y')),
    EqOp(Var('t1.x'), Var('t2.z')),
  )

  left_key, right_key = join_keys(SCHEMA_1,SCHEMA_2, multi_key)

  eq_(
    left_key((1,), ctx),
    (1,1)
  )

  eq_(
    right_key((1,0), ctx),
    (1,0)
  )

def test_hash_join():
  
  simple_op = EqOp(Var('t1.x'), Var('t2.y'))
  ctx = {}

  comparison = join_keys(SCHEMA_1,SCHEMA_2, simple_op)
  j = tuple(hash_join(t1,t2, comparison, ctx))

  eq_(
    j,
    (
      (1,1,0),
      (1,1,1),
    )
  )

  multi_key = And(
    EqOp(Var('t1.x'), Var('t2.y')),
    EqOp(Var('t1.x'), Var('t2.z')),
  )

  comparison = join_keys(SCHEMA_1,SCHEMA_2, multi_key)
  j = tuple(hash_join(t1,t2, comparison, ctx))

  eq_(
    j,
    (
      (1,1,1),
    )
  )
