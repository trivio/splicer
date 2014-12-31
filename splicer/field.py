class Field(object):
  __slots__ = {
    'name': "-> string [REQUIRED]",
    'type': "-> string [REQUIRED] integer|float|string|boolean|date|datetime|time|record",
    'mode': "-> string [OPTIONAL] REQUIRED|NULLABLE|REPEATED: default NULLABLE",
    'fields': "-> list [OPTIONAL IF type = RECORD]",
    'schema_name': "-> strnig [OPTIONAL]"
  }

  def __init__(self, **attrs):
    self.name = attrs['name']
    self.type = attrs['type']
    self.mode = attrs.get('mode', 'NULLABLE')
    self.schema_name = attrs.get('schema_name')
    self.fields = [
      f if isinstance(f, Field) else Field(**f)
      for f in attrs.get('fields', [])
    ]


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
      and self.schema_name == other.schema_name
    )

  @property
  def path(self):
    if self.schema_name:
      return self.schema_name + "." + self.name
    else:
      return self.name
  

  def new(self, **parts):
    attrs = {attr:getattr(self, attr) for attr in self.__slots__}
    attrs.update(parts)

    return self.__class__(**attrs)

  def to_dict(self):
    return dict(
      #schema_name = self.schema_name,
      name = self.name,
      type = self.type,
      mode = self.mode,
      fields = [f.to_dict() for f in self.fields]
    )


