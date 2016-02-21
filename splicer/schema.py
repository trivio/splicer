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
      field if isinstance(field, Field) else Field(schema_name=name,**field) 
      for field in fields
    ]

    self._field_map =  {f.name:f for f in self.fields}
    self._field_pos = { f.name:i for i,f in enumerate(self.fields) }


  def __repr__(self):
    name = self.name or "(no name)"
    return "Relation " + name + ":\n" + "\n".join([ 
      ("  {name}:[{type}]" if f.mode == 'REPEATED' else "  {name}:{type}").format(
        name = f.name,
        type = f.type
      )

       for f in self.fields
    ])

  def __eq__(self, other):
    """Two schemas equal if their fields equal"""

    if len(self.fields) != len(other.fields):
      return False

    return  all([f1 == f2 for f1, f2 in zip(self.fields, other.fields)])

  def __getitem__(self, field_name):
    return self.get_field(field_name)

  @property
  def field_map(self):
    return self._field_map
  

  def field_position(self, path):
    field = self.get_field(path)
    return self.fields.index(field)
 
  def get_field(self, path):
    parts = path.rsplit('.',1)
    if len(parts) == 1:
      name = parts[0]
      predicate = lambda f: f.name == name
    else:
      schema_name, name = parts
      predicate = lambda f: f.schema_name == schema_name and f.name == name

    fields = list(filter(predicate, self.fields))

    if len(fields) == 1:
      return fields[0]
    elif len(fields) == 0:
      raise RuntimeError('No such field "{}"'.format(path))
    else:
      raise RuntimeError('Field "{}" is ambigous'.format(path))
   
    

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
    

