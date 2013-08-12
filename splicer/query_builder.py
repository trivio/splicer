from . import Query
from .ast import (
  RelationalOp, ProjectionOp, SelectionOp, GroupByOp, OrderByOp, 
  SliceOp, JoinOp, LoadOp,
  And, SelectAllExpr
)
import query_parser

from .compilers.local import is_aggregate

class QueryBuilder(object):
  """
  Helps build a query 
  """

  __slots__ = {
    'dataset': '-> DataSet',
    'column_exps': 'str -- uparsed column',
    'load': '-> nullary op',
    'ordering': '-> [Field] -- results ',
    'grouping': '-> [Field]',
    'qualifiers': '-> str',
    'stop': "int",
    'start': "int"
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
    self.load = None
    self.qualifiers = ()
    self.ordering = None
    self.grouping = []
    self.start = None
    self.stop = None

  def __repr__(self):
    return repr(self.schema)

  def __iter__(self):
    return iter(self.execute())

  @property
  def schema(self):
    return self.query.schema

  def select(self, column_exps):
    return self.new(column_exps=column_exps)

  def frm(self, clause):
    relation = query_parser.parse_from(clause)
    return self.new(load = relation)

  def join(self, clause, on=None):
    if not self.load:
      raise ValueError('Specify at least one relation with frm(...) before using join')

    if isinstance(clause, QueryBuilder):
      load = JoinOp(self.load, clause.operations)
    else:
      load = query_parser.parse_join(clause, self.load)

    if on:
      load.bool_op = query_parser.parse(on)

    return self.new(load = load )


  def where(self, qualifiers):
    return self.new(qualifiers=self.qualifiers + (qualifiers,))

  def group_by(self, grouping_statement):
    exprs = query_parser.parse_group_by(grouping_statement)
    return self.new(grouping=exprs)

  def order_by(self, ordering_exp):
    ordering = query_parser.parse_order_by(ordering_exp)

    return self.new(ordering=ordering)

  def limit(self, limit):
    return self.new(stop=limit)

  def offset(self, offset):
    return self.new(start=offset)

  @property
  def query(self):
    """
    Returns a valid query suitable for execution, or raises an exception.
    """

    if not self.load:
      operations = LoadOp('')
    else:
      operations = self.load

    if self.qualifiers:
      qualifiers = iter(self.qualifiers)
      bool_op = query_parser.parse(qualifiers.next())
      for qualifier in qualifiers:
        bool_op = And(bool_op, query_parser.parse(qualifier))

      operations = SelectionOp(operations, bool_op)
      #operations.append(SelectionOp(bool_op))


    operations = query_parser.parse_select(operations, self.column_exps)


    if self.grouping or self.has_aggregates(operations):
      operations = GroupByOp(operations, *self.grouping)
    
    if self.ordering:
      # todo: eleminate ordering if it matches
      # the grouping since we already sort
      #operations.append(self.ordering)
      operations = OrderByOp(operations, *self.ordering)

    if self.stop is not None or self.start is not None:
      if self.start and self.stop:
        stop = self.start + self.stop
      else:
        stop = self.stop 
      operations = SliceOp(operations, self.start, stop)

    return Query(self.dataset,  operations)


  def has_aggregates(self, projection_op):
    """Returns true if the projection has aggregates"""
    if not isinstance(projection_op, ProjectionOp):
      return False

    for expr in projection_op.exprs:
      if is_aggregate(expr, self.dataset):
        return True
    else:
      return False

  @property
  def operations(self):
    return self.query.operations

  def dump(self):
    self.query.dump()

  def execute(self):
    return self.query.execute()

  def create_view(self, name):
    self.query.create_view(name)
    return self