from itertools import chain

from .immutable import ImmutableMixin
from .field import Field

class Schema(ImmutableMixin):
  __slots__ = {
    'name': '-> str',
    'fields': '-> [Field]',
    '_field_map': '-> {<name:str>: Field}',
    '_field_pos': '-> {<name:str>: postion:int}'
  }
  
  def __init__(self, fields, name='', **kw):
    self.name = name
    self.fields = [ 
      field if isinstance(field, Field) else Field(**field) 
      for field in fields
    ]

    self._field_map =  {f.name:f for f in self.fields}
    self._field_pos = { f.name:i for i,f in enumerate(self.fields) }



  def __eq__(self, other):
    """Two schemas equal if their fields equal"""

    if len(self.fields) != len(other.fields):
      return False

    return  all([f1 == f2 for f1, f2 in zip(self.fields, other.fields)])

  def __getitem__(self, field_name):
    return self.field_map[field_name]

  @property
  def field_map(self):
    return self._field_map

  def field_position(self, path):
    return self._field_pos[path]

  def to_dict(self):
    return dict(fields=[f.to_dict() for f in self.fields])


class JoinSchema(Schema):
  """
  Represents the schema produced by joining multiple schemas.
  """

  def __init__(self, *schemas):
    fields = [
      f.new(name=(schema.name + '.' + f.name) if schema.name else (f.name))
      for schema in schemas
      for f in schema.fields
    ]

    super(self.__class__,self).__init__(fields)
    # TODO: add field names that don't conflict to _field_pos
    

