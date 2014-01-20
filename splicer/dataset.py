from .query import Query, view_replacer
from .query_builder import QueryBuilder
from .query_parser import parse_statement
from .relation import NullRelation, NullAdapter
from .ast import LoadOp
from .aggregate import Aggregate
from .compilers import local
from .field import Field

from .operations import walk

from . import functions

class DataSet(object):

  def __init__(self):
    self.adapters = [NullAdapter()]

    self.relation_cache = {}

    self.views = {}
    self.schema_cache = {}
    self.executor = None
    self.compile = local.compile
    self.dump_func = None
    self.udfs = {}

    self.aggregates = {}
    
    functions.init(self)



  def add_adapter(self, adapter):
    """
    Add the given adapter to the dataset.

    Multiple adds for the instance of the same
    adapter are ignored.

    """

    if adapter not in self.adapters:
      self.adapters.append(adapter)

  def create_view(self, name, query_or_operations):
    if isinstance(query_or_operations, basestring):
      operations = self.query(query_or_operations).operations
    else:
      operations = query_or_operations

    self.views[name] = operations
    
  def aggregate(self, returns=None, initial=None, name=None, finalize=None):
    def _(func, name):
      if name is None:
        name = func.__name__
      self.add_aggregate(name, func, returns, initial, finalize)
      return func
    return _

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
      return func
    return _ 

  def add_aggregate(self, name, func, returns, initial, finalize=None):
    self.aggregates[name] = Aggregate(
      function=func, 
      returns=returns, 
      initial=initial,
      finalize=finalize
    )


  def add_function(self, name, function, returns=None):
    if name in self.udfs:
      raise ValueError("Function {} already registered".format(name))

    if returns:
      if callable(returns):
        function.returns = returns
      else:
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

  def get_view(self, name):
    view = self.views.get(name)
    if view:
      return replace_views(view,self)
    else:
      return None

  @property
  def relations(self):
    """
    Returns a list of all relations from all adapters
    note this could be a slow operation as remote
    calls must be made to each adapter. 

    As a side effect the relation_cache will be updated.
    """

    for adapter in self.adapters:
      for name, schema in adapter.relations:
        self.relation_cache[name] = schema
    return [item for item in self.relation_cache.items() if item[0] != '']



  def adapter_for(self, relation):
    for adapter in self.adapters:
      if adapter.has(relation):
        return adapter

  def get_relation(self, name):
    """Returns the relation for the given name.

    The dataset will search all adapters in the order the
    adapters were added to the dataset returning the first 
    relation with the given name.
    """
    relation = self.relation_cache.get(name)
    if relation is None:
      for adapter in self.adapters:
        relation = adapter.get_relation(name)
        if relation:
          self.relation_cache[name] = relation
          break

    return relation


  def get_schema(self, name):
    """
    Returns the schema for relation found with the given name.

    The search order is the same as dataset.get_relation()
    """
    return self.adapter_for(name).schema(name)

    #return self.get_relation(name).schema 

  def set_compiler(self, compile_fun):
    self.compile = compile_fun

  def set_dump_func(self, dump_func):
    self.dump_func = dump_func

  def dump(self, relation):
    self.dump_func(relation)

  def execute(self, query, *params):

    callable = self.compile(query)
    ctx = {
      'dataset': self,
      'params': params
    }

    return callable(ctx)


  def query(self, statement):
    """Parses the statement and returns a Query"""
    return Query(self, parse_statement(statement))

  def frm(self, relation_or_stmt):
    return QueryBuilder(self).frm(relation_or_stmt)

  def select(self, *cols):
    return QueryBuilder(self).select(*cols)


def replace_views(operation, dataset):
  def adapt(loc):
    node = loc.node()
    if isinstance(node, LoadOp):
      return view_replacer(dataset, loc, node)
    else:
      return loc
  return walk(operation, adapt)

