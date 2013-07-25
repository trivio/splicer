from .schema import Schema

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


  @property
  def fields(self):
    return self.schema.fields

  def __iter__(self):
    return self.iterator
