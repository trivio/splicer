import os
from os.path import join, getsize
import re
from itertools import chain

from splicer import Schema, Field
from splicer.path import pattern_regex
from splicer import codecs

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

    pattern = options.pop('pattern', None)
    if pattern:
      while pattern.startswith('/'):
        pattern = pattern[1:]

      self.pattern_regex, self.pattern_columns = pattern_regex(
        self.root_dir + pattern
      )

    else:
      self.pattern_regex = None
      self.pattern_columns = []

    self.content_column = options.pop('content_column', None)
    self.filename_column = options.pop('filename_column', None)
  
    self.decode = options.pop('decode', "none")

    self._schema = None
    if 'schema' in options:
      self._schema = Schema(**options.pop('schema'))

    if options:
      raise ValueError("Unrecognized options {}".format(options.keys()))


  @property
  def schema(self):
    if self._schema is None:
      fields = [
        Field(name=name, type="STRING") for name in self.pattern_columns
      ]

      if self.content_column:
        fields.append(Field(name=self.content_column, type='BINARY'))

      if self.filename_column:
        fields.append(Field(name=self.filename_column, type='STRING'))

      if self.decode != "none":
        fields.extend(
          self.fields_from_content(self.decode)
        )
      self._schema = Schema(name=self.name, fields=fields)


    return self._schema


  def files(self):
    return (
      join(root,f)
      for root, dirs, files in os.walk(self.root_dir)
      for f in files
    )

  def match_info(self):
    """
    Returns: tuple((<extracted1>,...,<extractedX>), path)
    for each file that matches the FileTable's pattern_regex.
    If no regex is specified returns tuple((), path) for all
    files under the root_dir.

    """

    if not self.pattern_regex:
      for path in self.files():
        yield (), path
    else:
      for path in self.files():
        m = self.pattern_regex.match(path)
        if m:
          yield m.groups(), path


  def fields_from_content(self, decode):
    """
    Returns the schema for the first matching file
    under the root_dir.
    """
    try:
      partition_data, path  = self.match_info().next()
    except StopIteration:
      return []
    relation = codecs.relation_from_path(path, decode)
    if relation:
      return relation.schema.fields
    else:
      # todo: consider defaulting to 'application/octet-stream'
      return []

  def extract_function(self):
    """
    Returns a function that will extract the data from a
    file path.
    """

    def identity(partition_info, path):
      yield partition_info

    funcs = [identity]

    if self.content_column:
      def contents(partition_info, path):
        with open(path) as f:
          yield partition_info + (f.read(),)

      funcs.append(contents)

    if self.filename_column:
      def filename(partition_info, path):
        yield  partition_info + (path,)

      funcs.append(filename)

    if self.decode != "none":
      def decode(partition_info, path):
        relation = codecs.relation_from_path(path, self.decode)
        return (
          partition_info + tuple(row)
          for row in relation
        )
      funcs.append(decode)

    if len(funcs) == 1:
      return funcs[0]

    def extract(partition_info, path):
      """
      Return one or more rows by composing the functions.
      """

      rows = funcs[0](partition_info,path)

      for f in funcs[1:]:
        rows = chain(*(
          iter(f(row, path))
          for row in rows
        ))

      return rows

    return extract



  def __iter__(self):
    extract = self.extract_function()

    for partition_info, path in self.match_info():
      for row in extract(partition_info, path):
        yield row


