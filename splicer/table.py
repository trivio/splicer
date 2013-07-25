from .schema import Schema

class Table(object):
  def __init__(self, server, name, schema):
    """

    Initialize a table with a name or a schema.

    Args:
      name (str):  The name of the table.
      schema (Schema | dict): Schema for the table specified as a dict
      or instance of the Schema class.

    """


    self.server = server
    self.name = name

    if isinstance(schema, dict):
      schema = Schema(**schema)
    self.schema = schema

  @property
  def fields(self):
    return self.schema.fields


  def __iter__(self):
    """
    Returns an iterator of tuples. 

    Table implementations from remote servers should use qualifiers
    and columns to reduce the set of results if they can. This will
    save network bandwidth or disk load time. Insitu will filter and 
    take the columns it needs from the rows returned by this method 
    regardless so Servers without filtering capabilities are free
    to return the data as is.
    """
    return iter([])