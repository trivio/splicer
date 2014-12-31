from collections import namedtuple

from splicer.ast import LoadOp

class Relation(namedtuple('Relation', 'adapter, name, schema, records')):
  """
  Represents a list of tuples
  """
  __slots__ = ()

  # equality testing mostly used during unit tests
  def __eq__(self,other):
   
    if isinstance(other, Relation):
      return self.adapter == other.adapter and self.name == other.name
    elif isinstance(other, LoadOp):
      return self.name  == other.name

  def __call__(self, ctx):
    return self.records(ctx)
