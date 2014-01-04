from functools import partial

from zipper import zipper

# functions for manipulating operations go here
from ast import LoadOp, JoinOp, EqOp, RelationalOp, Function, Var



def query_zipper(operation):
  return zipper(operation, is_branch, children, make_node)

def is_branch(operation):
  return not isinstance(operation, LoadOp)

def children(operation):
  if isinstance(operation, JoinOp):
    return (operation.left, operation.right)
  elif isinstance(operation, Function):
    return tuple(
      arg 
      for arg in operation.args 
      if isinstance(arg, RelationalOp) or isinstance(arg, Function)
    )
  else:
    return (operation.relation,)

def make_node(operation, children):
  if isinstance(operation, JoinOp):
    left, right = children
    return operation.new(left=left, right=right)
  elif isinstance(operation, Function):
    pos = 0
    args = []
    for arg in operation.args:
      if isinstance(arg, RelationalOp) or isinstance(arg, Function):
        args.append(children[pos])
        pos += 1
      else:
        args.append(arg)
    return operation.new(args=args)
  else:
    return operation.new(relation=children[0])




def walk(operation, visitor):
  """
  walk is a method, used to produce a new query plan based on an
  exsiting plan.  

  Parameters:
  -----------
  operation: current node being visited

  visitor: method that takes a single argument loc. 
           it's return value will be used in place of the visited
           loc. Methods that want to keep the tree as  is should
           return the loc.
  """
  loc = query_zipper(operation).leftmost_descendant()

  while True:
    loc = visitor(loc)
    if loc.at_end():
      break
    else:
      loc = loc.postorder_next()

  return loc.root()

def view_replacer(dataset, loc, op):
  view = dataset.get_view(op.name)
  if view:
    loc = loc.replace(view).leftmost_descendant()
  return loc


def replace_views(operation, dataset):
  def adapt(loc):
    node = loc.node()
    if isinstance(node, LoadOp):
      return view_replacer(dataset, loc, node)
    else:
      return loc
  return walk(operation, adapt)



