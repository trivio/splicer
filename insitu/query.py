from .schema_interpreter import interpret as interpret_schema
class Query(object):
  __slots__ = {
    'dataset': '-> DataSet',
    'operations': '-> [Operations]',
    'relation': 'Relation'
  }


  def __init__(self, dataset, relation, operations):
    self.dataset = dataset
    self.relation = relation
    self.operations = operations

  @property
  def schema(self):
    return interpret_schema(self.dataset, self.relation, self.operations)
    
  def execute(self, *params):
    self.dataset.execute(self, *params)
