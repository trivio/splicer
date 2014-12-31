from nose.tools import *

from splicer import  Schema, Field,Relation
from splicer import codecs

from StringIO import StringIO

def test_register_decoder():

  @codecs.decodes('text/plain')
  def decoder(stream):

    return (
      (line.rstrip(),)
      for line in stream
    )

  stream = StringIO("blah\nfoo,1\nbaz")
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
  stream = StringIO("field1,field2,field3\nfoo,1,0\nbaz,2,0")

  schema = codecs.schema_from(stream, mime_type='text/csv')
  
  eq_(
     schema,
     Schema([
       Field(name='field1', type='STRING'),
       Field(name='field2', type='STRING'),
       Field(name='field3', type='STRING')
     ])
  )


  relation = codecs.relation_from(stream, mime_type='text/csv')

  assert_sequence_equal(
    list(relation),
    [
      ['foo','1','0'],
      ['baz','2','0']
    ]
  )



