from .field import Field

class Schema(object):
  __slots__ = {
    'fields': '-> [Field]',
    '_field_map': '-> {<name:str>: Field}'
  }
  
  def __init__(self, fields):
    self.fields = [ 
      field if isinstance(field, Field) else Field(**field) 
      for field in fields
    ]

  def __eq__(self, other):
    """Two schemas equal if their fields equal"""

    if len(self.fields) != len(other.fields):
      return False

    return  all([f1 == f2 for f1, f2 in zip(self.fields, other.fields)])

  def __getitem__(self, field_name):
    return self.field_map[field_name]

  @property
  def field_map(self):
    fm = getattr(self, '_field_map', None)
    if fm is None:
      self._field_map = fm =  {f.name:f for f in self.fields}
    return fm

  def field_position(self, path):
    return [i for i,f in enumerate(self.fields) if f.name == path][0]

  def to_dict(self):
    return dict(fields=[f.to_dict() for f in self.fields])



