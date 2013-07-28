from ast import ProjectionOp, GroupByOp, Function

from .schema_interpreter import interpret as interpret_schema
class Query(object):
  __slots__ = {
    'dataset': '-> DataSet',
    'operations': '-> [Operations]',
    'relation_name': 'str'
  }


  def __init__(self, dataset, relation_name, operations):
    self.dataset = dataset
    self.relation_name = relation_name
    self.operations = operations


  def __iter__(self):
    return self.execute()


  @property
  def schema(self):
    schema = self.dataset.get_schema(self.relation_name)
    return interpret_schema(self.dataset, schema, self.operations)
    
  def execute(self, *params):
    return self.dataset.execute(self, *params)




