import os
from os.path import join
from itertools import chain

from ..relation import Relation
from ..schema import Schema
from .. import codecs
from splicer.path import pattern_regex


def init(dataset):
  dataset.add_function("files", files)
  dataset.add_function("decode", decode)
  dataset.add_function("contents", contents)
  dataset.add_function("extract_path", extract_path)


def contents(relation, path_column, content_column='contents'):
  """
  Given a relation and a path_column, returns a new relation
  whose rows are the same as the original relation with the
  addition of the contents of the file specified by path_column.

  Note: This method is not  suitable for large files,
  as entire contents of the file are read into memory.
  """
  field_pos = relation.schema.field_position(path_column)
 

  return Relation(
    Schema(relation.schema.fields + [dict(type='BINARY', name=content_column)]),
    (
      row + (open(row[field_pos]).read(), )
      for row in relation
    )
  )

def decode(relation, mime_type,  path_column="path", schema=None):
  field_pos = relation.schema.field_position(path_column)
  relation_from_path = codecs.relation_from_path

  if schema is None:
    it = iter(relation)
    first = next(it)

    schema = Schema(
      relation.schema.fields + 
      relation_from_path(first[field_pos]).schema.fields
    )
    relation = chain((first,), it)

  return Relation(
    schema,
    (
      r + tuple(s)
      for r in relation
      for s in relation_from_path(r[field_pos], mime_type)
    )
  )


def files(root_dir, filename_column="path"):
  """
  Return an iterator of all filenames starting at root_dir or below
  """ 

  return Relation(
    Schema([dict(type="STRING", name=filename_column)]),
    (
      (join(root,f), )
      for root, dirs, files in os.walk(root_dir)
      for f in files
    )
  )

def extract_path(files, pattern, path_column="path"):
  """
  Extracts patterns out of file paths and urls.

  Returns a relation where the path_column is matched 
  against a reular expression expressed by the pattern
  argument.
  the resulting group info appened to the matching row.

  Example
  ['/some/path'] -> ['/some/path', 'some', 'path']
  """

  field_pos = files.schema.field_position(path_column)
  regex, columns = pattern_regex(pattern)

  schema = Schema(files.schema.fields + [
    dict(name=c, type='STRING')
    for c in columns    
  ])

  def extract():
    for row in files:
      path = row[field_pos]
      m = regex.match(path)
      if m:
        yield row + m.groups()

  return Relation(schema, extract())

