class Server(object):

  def tables(self):
    """
    May return a list of -some- of the tables the server supports.
    Some Servers like HTTP etc.. will create tables on the fly
    based on the passed in URL
    """
    
  def get_table(self, name):
    """Return the table with the given name or None if this
    server does not have the given table."""