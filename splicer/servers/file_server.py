import os
from os.path import join, getsize
import re

from splicer import Schema, Field
from splicer.path import pattern_regex


class FileServer(object):
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

class FileTable(object):
  def __init__(self,  name, root_dir, **options):
    self.name = name

    if not root_dir.endswith('/'):
      root_dir += '/'
    self.root_dir = root_dir

    pattern = options.get('pattern')
    if pattern:
      while pattern.startswith('/'):
        pattern = pattern[1:]

      self.pattern_regex, columns = pattern_regex(self.root_dir + pattern)
    else:
      self.pattern_regex = None
      columns = []


    fields = [
      Field(name=name, type="STRING") for name in columns
    ]

    self.content_column = options.get('content_column')
    if self.content_column:
      fields.append(Field(name=self.content_column, type='BINARY'))

    self.filename_column = options.get('filename_column')
    if self.filename_column:
      fields.append(Field(name=self.filename_column, type='STRING'))

    self.schema = Schema(fields)

  
  def extract_function(self):
    """
    Returns a function that will extract the data from a
    file path.
    """

    funcs = []
    if self.pattern_regex:
      def pattern_extractor(path):
        m = self.pattern_regex.match(path)
        if m:
          return m.groups()
        else:
          return None
      funcs.append(pattern_extractor)

    if self.content_column:
      def read(path):
        with open(path) as f:
          return (f.read(),)

      funcs.append(read)

    if self.filename_column:
      funcs.append(lambda path: (path,))

    if funcs:
      def extract(path):
        return tuple(
          c
          for f in funcs
          for c in f(path)
        )

      return extract
    else:
      return lambda path: tuple()

  
  def __iter__(self):
    extract = self.extract_function()

    for root, dirs, files in os.walk(self.root_dir):
      for path in (join(root,f) for f in files):
        parts = extract(path)
        if parts is not None:
          yield parts

 
