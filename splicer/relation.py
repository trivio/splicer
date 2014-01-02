from .schema import Schema
from .servers import Adapter

class Relation(object):
  def __init__(self, schema, iterator):
    """

    Endow an interable with a schema so that's it's suitable
    to be used as a relation

    Args:
      schema (Schema):  The schema for an iterable
      iterator (iterator): An iterable object 

    """

    self.schema = schema
    self.iterator = iterator


  def __iter__(self):
    return self.iterator

class NullAdapter(Adapter):
  def has(self, relation):
    if relation == '':
      return True

  def table_scan(self, name, ctx):
    return NullRelation()


# TODO: deprecate this
class NullRelation(object):
  """Relation used for queries that don't involve tables"""
  schema = Schema(name="", fields=[])
  
  def __iter__(self):
    return iter(((),))

