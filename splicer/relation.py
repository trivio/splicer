from collections import namedtuple

class Relation(namedtuple('Relation', 'adapter, name, schema, records')):
  """
  Represents a list of tuples
  """
  __slots__ = ()

  def __eq__(self,other):
    # equal if adapter and name are equal
    # using slice notation in case we're compared to a tuple
    return self[:2] == other[:2]
  def __call__(self, ctx):
    return self.records(ctx)
