from .schema import Schema

class Table(object):
  def __init__(self, name, schema):
    """

    Initialize a table with a name or a schema.

    Args:
      name (str):  The name of the table.
      schema (Schema | dict): Schema for the table specified as a dict
      or instance of the Schema class.

    """

    self.name = name

    if isinstance(schema, dict):
      schema = Schema(**schema)
    self.schema = schema

  @property
  def fields(self):
    return [field for field in self.schema.fields]