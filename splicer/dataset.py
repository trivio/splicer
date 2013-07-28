from .query import Query
from .query_builder import QueryBuilder

from aggregate import Aggregate
from .compilers import local
from .field import Field

class DataSet(object):

  def __init__(self):
    self.servers = []
    self.relation_cache = {}
    self.schema_cache = {}
    self.executor = None
    self.compile = local.compile
    self.udfs = {}

    self.aggregates = {
      "count": Aggregate(
        function=lambda state: state + 1,
        returns=Field(name="count", type="INTEGER"),
        initial=0
      )
    }



  def add_server(self, server):
    """
    Add the given server to the dataset.

    Multiple adds for the instance of the same
    relation are ignored.

    """

    if server not in self.servers:
      self.servers.append(server)


  def function(self, returns=None, name=None):
    """Decorator for registering functions

    @dataset.function
    def somefunction():
      pass


    """

    def _(func, name=name):
      if name is None:
        name = func.__name__
      self.add_function(name, func, returns)
    return _ 



  def add_function(self, name, function, returns=None):
    if returns:
      function.returns = Field(**returns)
    else:
      function.returns = None


    self.udfs[name] = function

  def get_function(self, name):
    function = self.udfs.get(name) or self.aggregates.get(name)
    if function:
      return function
    else:
      raise NameError("No function named {}".format(name))

  @property
  def relations(self):
    """
    Returns a list of all relations from all servers
    note this could be a slow operation as remote
    calls must be made to each server. 

    As a side effect the relation_cache will be updated.
    """

    for server in self.servers:
      for name, schema in server.relations:
        self.relation_cache[name] = schema
    return self.relation_cache.items()


  def has(self, name):
    return self.get_relation(name)

  def get_relation(self, name):
    """Returns the relation for the given name.

    The dataset will search all servers in the order the
    servers were added to the dataset returning the first 
    relation with the given name.
    """
    relation = self.relation_cache.get(name)
    if relation is None:
      for server in self.servers:
        relation = server.get_relation(name)
        if relation:
          self.relation_cache[name] = relation
          break

    return relation


  def get_schema(self, name):
    """
    Returns the schema for relation found with the given name.

    The search order is the same as dataset.get_relation()
    """

    return self.get_relation(name).schema

 

  def set_compiler(self, compile_fun):
    self.compile = compile_fun


  def execute(self, query, *params):

    callable = self.compile(query)
    ctx = {
      'dataset': self,
      'params': params
    }

    return callable(ctx)

  def query(self, statement):
    """Parses the statement and returns a Query"""
    return Query.parse(self, statement)

  def frm(self, relation_name):
    return QueryBuilder(self).frm(relation_name)

  def select(self, *cols):
    return QueryBuilder(self).select(*cols)

