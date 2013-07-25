from . import Query
from .ast import SelectionOp, And, SelectAllExpr
import query_parser


class QueryBuilder(object):
  """
  Helps build a query 
  """

  __slots__ = {
    'dataset': '-> DataSet',
    'column_exps': 'str -- uparsed column',
    'relation_name': '-> str -- the root relation',
    'ordering': '-> [Field] -- results ',
    'grouping': '-> [Field]',
    'qualifiers': '-> str'
  }


  def new(self, **parts):
    derived_qb = self.__class__(self.dataset)

    for attr in self.__slots__:
      setattr(derived_qb, attr, getattr(self, attr, None))

    for attr, value in parts.items():
      setattr(derived_qb, attr, value)
    return derived_qb


  def __init__(self, dataset):
    self.dataset = dataset
    self.column_exps = "*"
    self.relation_name = None
    self.qualifiers = ()
    self.ordering = None
    self.grouping = None

  def __iter__(self):
    return iter(self.execute())

  @property
  def schema(self):
    return self.query.schema

  def select(self, column_exps):
    return self.new(column_exps=column_exps)

  def frm(self, relation_name):
    if not self.dataset.has(relation_name):
      raise ValueError, "No such relation {0}".format(relation_name)

    return self.new(relation_name=relation_name)

  def where(self, qualifiers):
    return self.new(qualifiers=self.qualifiers + (qualifiers,))

  def group_by(self, *grouping):
    return self.new(grouping=grouping)

  def order_by(self, ordering_exp):
    ordering = query_parser.parse_order_by(ordering_exp)

    return self.new(ordering=ordering)

  def limit(self, limit):
    return self.new(limit=limit)

  def offset(self, offset):
    return self.new(offset=offset)

  @property
  def query(self):
    """
    Returns a valid query suitable for execution, or raises an exception.
    """

    if not self.relation_name:
      raise ValueError('Need to specify at least one relation')

    operations = []

    if self.qualifiers:
      qualifiers = iter(self.qualifiers)
      bool_op = query_parser.parse(qualifiers.next())
      for qualifier in qualifiers:
        bool_op = And(bool_op, query_parser.parse(qualifier))

      operations.append(SelectionOp(bool_op))

    if self.ordering:
      operations.append(self.ordering)

    projection_op = query_parser.parse_select(self.column_exps)

    is_select_star = (
      len(projection_op.exprs) == 1
      and isinstance(projection_op.exprs[0], SelectAllExpr)
      and projection_op.exprs[0].table is None

    )
    if not is_select_star:
      operations.append(projection_op)

    return Query(self.dataset, self.relation_name, operations)


  def execute(self):
    return self.query.execute()
