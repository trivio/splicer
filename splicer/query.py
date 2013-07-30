from ast import ProjectionOp, GroupByOp, Function

from .schema_interpreter import interpret as interpret_schema
class Query(object):
  __slots__ = {
    'dataset': '-> DataSet',
    'operations': '-> [Operations]',
  }


  def __init__(self, dataset,  operations):
    self.dataset = dataset
    self.operations = operations


  def __iter__(self):
    return iter(self.execute())


  @property
  def schema(self):
    return interpret_schema(self.dataset,  self.operations)
    
  def execute(self, *params):
    return self.dataset.execute(self, *params)




