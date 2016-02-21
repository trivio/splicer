from splicer import Table
from . import Adapter

class DictAdapter(Adapter):
  """
  An adapter for working with lists of dictionaries.
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


  def has(self, relation):
    return relation in self._tables

  def schema(self, relation):
    return self._tables[relation].schema

  def get_relation(self, name):
    return self._tables.get(name)

  def table_scan(self, name, ctx):
    return self._tables[name]



class DictTable(Table):
  def __init__(self, adapter, name, schema, rows):
    super(self.__class__, self).__init__(adapter, name, schema)
    self.key_index = [
      (f.name, () if f.mode == 'REPEATED' else None)
      for f in self.schema.fields
    ]
    self._rows = rows


  def __iter__(self):
    key_index = self.key_index

    return (
      tuple(row.get(key, default) for key, default in key_index)
      for row in self._rows
    )
