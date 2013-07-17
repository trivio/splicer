from . import Query
from .relational_ops import SelectionOp
import query_parser


class QueryBuilder(object):
  """
  Helps build a query 
  """

  __slots__ = {
    'dataset': '-> DataSet',
    'column_exps': 'str -- uparsed column',
    'relations': '-> [Relation] -- list of relations that will be queried',
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
    self.relations = ()
    self.qualifiers = ()
    self.ordering = None
    self.grouping = None


  def select(self, column_exps):
    return self.new(column_exps=column_exps)

  def frm(self, relation):
    if isinstance(relation, basestring):
      relation = self.dataset.get_relation(relation)
      if relation is None:
        raise ValueError, "No such relation {0}".format(relation)
    return self.new(relations=self.relations + (relation,))

  def where(self, qualifiers):
    return self.new(qualifiers=self.qualifiers + (qualifiers,))

  def group_by(self, *grouping):
    return self.new(grouping=grouping)

  def order_by(self, *ordering):
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

    if not self.relations:
      raise ValueError('Need to specify at least one relation')


    project_op = query_parser.parse_select(
      self.column_exps, 
      self.dataset, 
      self.relations
    )


    selection_op = SelectionOp(self.relations[0].schema)

    operations = [selection_op, project_op]

    return Query(self.dataset, project_op.schema, operations, self.relations[0])


  def execute(self):
    return self.query.execute()
