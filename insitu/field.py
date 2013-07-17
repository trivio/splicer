class Field(object):
  __slots__ = {
    'name': "-> string [REQUIRED]",
    'type': "-> string [REQUIRED] integer|float|string|boolean|date|datetime|time|record",
    'mode': "-> string [OPTIONAL] REQUIRED|NULLABLE|REPEATED: default NULLABLE",
    'fields': "-> list [OPTIONAL IF type = RECORD]",
    'getter': "-> function(row,ctx) -> object"
  }

  def __init__(self, **attrs):
    self.name = attrs['name']
    self.type = attrs['type']
    self.mode = attrs.get('mode', 'NULLABLE')
    self.fields = attrs.get('fields', [])

    # Todo: consider making a subclass for this
    self.getter = attrs.get('getter', None)

  def __repr__(self):
    return "<Field(name={name}, type={type} at {id}>".format(
      id=id(self),
      name=self.name,
      type=self.type
    )
      

  def __eq__(self, other):
    return (
      self.name == other.name
      and self.type == other.type
      and self.mode == other.mode
      and self.fields == other.fields
    )

  def new(self, **parts):
    attrs = {attr:getattr(self, attr) for attr in self.__slots__}
    attrs.update(parts)

    return self.__class__(**attrs)


