class Server(object):
  """
  Servere objects provide tables to the dataset.
  """

  def relations(self):
    """
    May return a list of name and schema of -some- of the relations 
    the server supports.
    
    Some Servers like HTTP etc.. will create tables on the fly
    based on the passed in URL so introspection is not possible
    """
    
    
  def get_table(self, name):
    """Return the relation (table, view, etc..) with the given name or None if this
    server does not have the given table."""