from splicer import Table

class MockServer(object):
  def __init__(self):
    
    table = Table(
      name = 'bogus',
      schema = dict(
        fields = [
          dict(
            name='x',
            type='INTEGER'
          ),
          dict(
            name='y',
            type='INTEGER'
          )
        ]
      )
    )

    self._tables = {
      table.name: table  
    }

  @property
  def tables(self):
    return self._tables.values()

  def get_table(self, name):
    return self._tables.get(name)
