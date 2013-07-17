from .field import Field

class Schema(object):
  __slots__ = {
    'fields': '-> [Field]'
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



