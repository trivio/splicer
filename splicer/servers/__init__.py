from functools import partial 
class Adapter(object):
  """
  Servere objects provide tables to the dataset.
  """

  @property
  def relations(self):
    """
    May return a list of name and schema of -some- of the relations 
    the server supports.
    
    Some Servers like HTTP etc.. will create tables on the fly
    based on the passed in URL so introspection is not possible
    """
    return []
    
    
  def get_relation(self, name):
    """Return the relation (table, view, etc..) with the given name or None if this
    server does not have the given table."""

  def has(self, relation):
    """Return true if the Adapter can resolve the relation"""

  def table_scan(self, name, ctx):
    raise NotImplemented()

  def evaluate(self, loc):
    return loc.replace(partial(self.table_scan, loc.node().name))