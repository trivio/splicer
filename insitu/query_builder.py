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

    if cols:
      if cols == '*':
        cols = ','.join(self.__schema__)

      self.col_exps = codd.parse(
        "({})".format(cols), 
        get_value=self.get_value
      ).func_closure[0].cell_contents


      #self.col_exps = [
      #  codd.parse(col, get_value=self.get_value)
      #  for col in cols
      #]

      self.reducers = [
        (pos, self.aggregates[col.__name__])
        for pos, col in enumerate(self.col_exps)
        if col.__name__ in self.aggregates
      ]
 
      self.schema = [
        getattr(c, '__name__', "col{}".format(i))
        for i,c in enumerate(self.col_exps)
      ]
      result_class = self.result_class = namedtuple("row", self.schema)


    self.cols = cols
    return self


  def execute(self):
    return self.query.execute()