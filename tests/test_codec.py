from nose.tools import *

from splicer import  Schema, Field,Relation
from io import StringIO

from splicer import codecs

def test_register_decoder():

  @codecs.decodes('text/plain')
  def decoder(stream):

    return (
      (line.rstrip(),)
      for line in stream
    )

  stream = StringIO(u"blah\nfoo,1\nbaz")
  relation = codecs.relation_from(stream, mime_type='text/plain')

  eq_(
    list(relation),
    [
      ('blah',),
      ('foo,1',),
      ('baz',)
    ]
  )

def test_decode_csv():
  stream = StringIO(u"field1,field2,field3\nfoo,1,0\nbaz,2,0")

  schema = codecs.schema_from(stream, mime_type='text/csv')

  expected = Schema([
      Field(name='field1', type='STRING'),
      Field(name='field2', type='STRING'),
      Field(name='field3', type='STRING')
  ])

  eq_(schema, expected)


def test_decode_csv_relations():
  stream = StringIO(u"field1,field2,field3\nfoo,1,0\nbaz,2,0")
  relation = codecs.relation_from(stream, mime_type='text/csv')

  assert_sequence_equal(
    list(relation),
    [
      ['foo','1','0'],
      ['baz','2','0']
    ]
  )
