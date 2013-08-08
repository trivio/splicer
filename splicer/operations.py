# functions for manipulating operations go here
from ast import LoadOp, JoinOp

def replace_views(operations, dataset):
  def view_replacer(node):
    if isinstance(node, LoadOp):
      view = dataset.get_view(node.name)
      if view:
        return view

    return node

  return walk(operations, view_replacer)


def walk(operation, visitor):
  """
  walk is method used to produce a new query plan based on an
  exsiting plan.  

  Parameters:
  -----------
  operation: current node being visited

  visitor: method that takes a single arguments node 
           it's return value will be used in place of the visited
           node. Methods that want to keep the tree as  is should
           return the node.
  """
  if isinstance(operation, LoadOp):
    # reached the bottom
    return visitor(operation)
  elif isinstance(operation, JoinOp):
    left = walk(operation.left, visitor)
    right = walk(operation.right, visitor)
    return visitor(operation.new(left=left, right=right))
  else:
    child = walk(operation.relation, visitor)
    return visitor(operation.new(relation=child))
