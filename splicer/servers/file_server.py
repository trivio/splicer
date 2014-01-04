from splicer import Schema, Field
from splicer.servers import Adapter
from splicer.ast import Function, Const

class FileServer(Adapter):
  def __init__(self, **relations):
    self._relations = {
      name:FileTable(name, **args) for name,args in relations.items()
    }

  @property
  def relations(self):
    return [
      (name, relation.schema)
      for name, relation in self._relations.items()
    ]

  def get_relation(self, name):
    return self._relations.get(name)

  def table_scan(self, name, ctx):
    return self._relations.get(name)

  def has(self, name):
    return self._relations.has_key(name)

  def evaluate(self, loc):
    relation = self._relations[loc.node().name]

    op = Function(
      'files', 
      Const(relation.root_dir)
    )

    if relation.pattern:
      op = Function('extract_path', op, Const(relation.root_dir + relation.pattern))

    if relation.content_column:
      op = Function('contents', op, Const(relation.content_column))

    if relation.decode != 'none':
      op = Function('decode', op, Const(relation.decode))

    return loc.replace(op).leftmost_descendant()



class FileTable(object):
  def __init__(self,  name, root_dir, **options):
    self.name = name

    if not root_dir.endswith('/'):
      root_dir += '/'
    self.root_dir = root_dir

    self.pattern  = options.pop('pattern', None)

    self.content_column = options.pop('content_column', None)
    self.filename_column = options.pop('filename_column', None)
  
    self.decode = options.pop('decode', "none")

    schema = options.pop('schema',None)
    self.schema = schema and Schema(**schema)

    if options:
      raise ValueError("Unrecognized options {}".format(options.keys()))


