import os
from nose.tools import eq_

from splicer.operations import query_zipper
from splicer import Relation
from splicer.ast import LoadOp

def compare(op1, op2):
  loc1 = query_zipper(op1).leftmost_descendant()
  loc2 = query_zipper(op2).leftmost_descendant()

  while True:
    n1 = loc1.node()
    n2 = loc2.node()

    if not (compare_relation(n1,n2)  or n1 == n2):
      raise NodeDiffException(n1,n2)

    if any((loc1.at_end(), loc2.at_end())):
      # if either is at the end, they both should be
      assert loc1.at_end() == loc2.at_end()
      break
    else:
      loc1 = loc1.postorder_next()
      loc2 = loc2.postorder_next()

def compare_relation(op1, op2):
  types = map(type, (op1, op2))

  if types in [[LoadOp, Relation], [Relation, LoadOp]]:
    return op1.name == op2.name
  else:
    return False

def fixture_path(name=""):
  d = os.path.dirname(__file__)
  return os.path.join(*[d,'fixtures', name])


class NodeDiffException(ValueError):
  def __init__(self, n1,n2):
    # figure out how they differ

    if type(n1) != type(n2):
      self.args = [
        'Nodes have different types node1: {} node2: {}'.format(type(n1), type(n2))
      ]
    else:
      for  attr in n1.__slots__:
        if attr == 'schema': continue
        a1 = getattr(n1, attr)
        a2 = getattr(n2, attr)

        if a1 != a2:
          self.args = [
            'Nodes have different attribute {}: {} != {}'.format(
             attr, 
              repr(a1), 
              repr(a2)
            )
          ]
          break

