class Query(object):
  __slots__ = {
    'schema': 'Schema',
    'column_names': '-> [str] list of column name',
    #'column_exps' : 'List of column exp objects',
    'dataset': '-> DataSet',
    'operations': '-> [Operations]',
    'relation': 'Relation'
  }


  def __init__(self, dataset, schema, operations, relation):
    self.dataset = dataset
    self.schema = schema
    self.operations = operations
    self.relation = relation

  def execute(self, *params):
    ctx = {
      'params': params,
      'udf': {}
    }

    relation = self.relation
    for op in self.operations:
      relation = op(relation, ctx)
  
    return relation

