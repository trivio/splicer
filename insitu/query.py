class Query(object):
  __slots__ = {
    'column_exp': 'str uparsed column',
    'column_names': '-> [str] list of column name',
    #'column_exps' : 'List of column exp objects',
    'dataset': '-> DataSet',
  }

  @classmethod
  def parse(cls, dataset, statement):
    pass


  def __init__(self, dataset):
    self.dataset = dataset


  def validate(self):
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
    return
