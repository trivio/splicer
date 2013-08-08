from sys import getsizeof

from nose.tools import *

from splicer.compilers.join import (
  nested_block_join,
  buffered,
  record_size
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

  j = tuple(nested_block_join(r,s, lambda r,ctx: True, {}))

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
