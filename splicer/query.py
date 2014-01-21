from .ast import LoadOp
from .operations import isa
from .schema_interpreter import resolve_schema

class Query(object):
  __slots__ = {
    'dataset': '-> DataSet',
    'operations': 'ast.Expr',
    'schema': 'Schema'
  }


  def __init__(self, dataset,  operations):
    self.dataset = dataset
    self.operations = resolve_schema(
      dataset, 
      operations, 
      (isa(LoadOp), view_replacer)
    )

    self.schema = self.operations.schema
 
  def __iter__(self):
    return iter(self.execute())
    
  def dump(self):
    self.dataset.dump(self.execute())

  def create_view(self, name):
    self.dataset.create_view(name, self.operations)
    
  def execute(self, *params):
    return self.dataset.execute(self, *params)



def view_replacer(dataset, loc, op):
  view = dataset.get_view(op.name)
  if view:
    loc = loc.replace(view).leftmost_descendant()
  return loc



