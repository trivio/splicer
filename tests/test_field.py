# test_schema_interpreter.py

from nose.tools import *


from splicer.field import Field


def test_to_dict():

  assert_dict_equal(
    Field(name='x', type="STRING").to_dict(),
    dict(name='x', type='STRING', mode="NULLABLE", fields=[])
  )
