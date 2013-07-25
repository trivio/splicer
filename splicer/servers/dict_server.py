from splicer import Table

class DictServer(object):
  """
  A server for working with lists of dictionaries.
  """
  def __init__(self, **tables):
    """

    Examples:
    Dictionary(
      users=[dict(),dict(),...],
      other=dict(
        schema=[],
        rows=[dict(),dict(),...]
      )
    )

    """
    self._tables = {}

    for name, table in tables.items():
      if isinstance(table, dict):
        schema = table['schema']
        rows=table['rows']
      else:
        rows = table
        schema = self.guess_schema(rows)

      self._tables[name] = DictTable(
        self,
        name, 
        schema=schema, 
        rows=rows
      )


  @property
  def relations(self):
    return [
      (name, table.schema)
      for name, table in self._tables.items()
    ]

  def get_relation(self, name):
    return self._tables.get(name)



class DictTable(Table):
  def __init__(self, server, name, schema, rows):
    super(self.__class__, self).__init__(server, name, schema)
    self.key_index = [f.name for f in self.schema.fields]
    self._rows = rows


  def __iter__(self):
    key_index = self.key_index

    return (
      tuple(row.get(key) for key in key_index)
      for row in self._rows
    )
