import os
from os.path import join
from itertools import chain

from ..schema import Schema
from ..codecs import schema_from_path, relation_from_path
from splicer.path import pattern_regex, regex_str


def init(dataset):
  dataset.add_function("files", files, files_schema)
  dataset.add_function("decode", decode, decode_schema)
  dataset.add_function("contents", contents, contents_schema)
  dataset.add_function("extract_path", extract_path, extract_path_schema)


def contents((schema, relation), path_column, content_column='contents'):
  """
  Given a relation and a path_column, returns a new relation
  whose rows are the same as the original relation with the
  addition of the contents of the file specified by path_column.

  Note: This method is not  suitable for large files,
  as entire contents of the file are read into memory.
  """

  field_pos = schema.field_position(path_column)
 
  return (
    row + (open(row[field_pos]).read(), )
    for row in relation
  )

def contents_schema(schema, path_column, content_column='contents'):
  return Schema(schema.fields + [dict(type='BINARY', name=content_column)])
  

def decode((schema, relation), mime_type, schema_or_path, path_column="path"):
  """
  Takes a relation that has a column which contains a path to a file.
  Returns one row for each row found in each file.

  Ex:
  [
    ('file1',),
    ('file2',)
  ] 

  - >

  [
    ('file1', 'col 1', 'col2', 'colx'),
    ('file1', 'col 1', 'col2', 'colx'),
    ('file1', 'col 1', 'col2', 'colx'),
    ('file2', 'col 1', 'col2', 'colx'),
    ('file2', 'col 1', 'col2', 'colx'),
  ]


  """
  #relation_from_path = codecs.relation_from_path
  field_pos = schema.field_position(path_column)

  return (
    r + tuple(s)
    for r in relation
    for s in relation_from_path(r[field_pos], mime_type)
  )

def decode_schema(schema, mime_type, schema_or_path, path_column="path"):
  #relation_from_path = codecs.schema_from_path
  
  if isinstance(schema_or_paths, Schema):
    return schema_or_paths
  else:
    return Schema(
      schema.fields + 
      schema_from_path(schema_or_path).fields
    )


def files(root_dir, filename_column="path"):
  """
  Return an iterator of all filenames starting at root_dir or below
  """ 

  return (
    (join(root,f), )
    for root, dirs, files in os.walk(root_dir)
    for f in files if not f.startswith('.')
  )
 
def files_schema(root_dir, filename_column="path"):
  return Schema([dict(type="STRING", name=filename_column)])

def extract_path((schema,files), pattern, path_column="path"):
  """
  Extracts patterns out of file paths and urls.

  Returns a relation where the path_column is matched 
  against a reular expression expressed by the pattern
  argument.
  the resulting group info appened to the matching row.

  Example
  ['/some/path'] -> ['/some/path', 'some', 'path']
  """

  field_pos = schema.field_position(path_column)
  regex, columns = pattern_regex(pattern)


  def extract():
    for row in files:
      path = row[field_pos]
      m = regex.match(path)
      if m:
        yield row + m.groups()

  return extract()

def extract_path_schema(schema, pattern, path_column="path"):
  regex, columns = pattern_regex(pattern)

  return Schema(schema.fields + [
    dict(name=c, type='STRING')
    for c in columns    
  ])


