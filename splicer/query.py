from .schema_interpreter import interpret as interpret_schema

class Query(object):
  __slots__ = {
    'dataset': '-> DataSet',
    'operations': 'ast.Expr',
  }


  def __init__(self, dataset,  operations):
    self.dataset = dataset
    self.operations = operations


  def __iter__(self):
    return iter(self.execute())


  @property
  def schema(self):
    return interpret_schema(self.dataset,  self.operations)

    
  def dump(self):
    self.dataset.dump(self.execute())

  def create_view(self, name):
    self.dataset.create_view(name, self.operations)
    
  def execute(self, *params):
    return self.dataset.execute(self, *params)





