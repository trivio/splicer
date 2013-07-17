class Op(object):

  def __init__(self, schema):
    self.schema = schema

  def __call__(self, relation, params):
    raise NotImplemented


class ProjectionOp(Op):
  def __init__(self, schema, *getters):
    super(self.__class__,self).__init__(schema)
    self.getters = getters

  def __call__(self, relation, ctx):
    getters = self.getters

    return (
      tuple(getter(row, ctx) for getter in getters)
      for row in relation
    )

class SelectionOp(Op):
  def __init__(self, schema, bool_op=None):
    super(self.__class__,self).__init__(schema)
    self.bool_op = bool_op

  def __call__(self, relation, ctx):
    row_iter = relation.rows(None, None)
    if self.bool_op is None:
      return row_iter
    else:
      return (
        row
        for row in row_iter
        if bool_op(row, ctx)
      )