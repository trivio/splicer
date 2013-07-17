from .query import Query
from .query_builder import QueryBuilder

class DataSet(object):

  def __init__(self):
    self.servers = []
    self.relation_cache = {}


  def add_server(self, server):
    """
    Add the given server to the dataset.

    Multiple adds for the instance of the same
    relation are ignored.

    """

    if server not in self.servers:
      self.servers.append(server)

  @property
  def relations(self):
    """
    Returns a list of all tabels from all servers
    note this could be a slow operation as remote
    calls must be made to each server. 

    As a side effect the relation_cache will be updated.
    """

    for server in self.servers:
      for relation in server.tables:
        self.relation_cache[relation.name] = relation
    return self.relation_cache.items()


  def get_relation(self, name):
    """
    Returns the first relation found with the given name.

    The dataset will search all servers in the order the
    servers were added to the dataset.
    """

    relation = self.relation_cache.get(name)
    if relation is None:
      for server in self.servers:
        relation = server.get_table(name)
        if relation:
          self.relation_cache[name] = relation
          break

    return relation

  def get_field(self, name):
    """
    Return the field object associated
    """

  def query(self, statement):
    """Parses the statement and returns a Query"""
    return Query.parse(self, statement)

  def select(self, *cols):
    return QueryBuilder(self).select(*cols)

  def udfs(self):
    return {}
