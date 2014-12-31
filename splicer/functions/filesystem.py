import os
from os.path import join
from itertools import chain

from .. import Relation
from ..schema import Schema
from ..codecs import schema_from_path, relation_from_path
from splicer.path import pattern_regex, regex_str


def init(dataset):
  dataset.add_function("files", files, files_schema)
  dataset.add_function("decode", decode, decode_schema)
  dataset.add_function("contents", contents, contents_schema)
  dataset.add_function("extract_path", extract_path, extract_path_schema)


def contents(ctx, relation, path_column, content_column='contents'):
  """
  Given a relation and a path_column, returns a new relation
  whose rows are the same as the original relation with the
  addition of the contents of the file specified by path_column.

  Note: This method is not  suitable for large files,
  as entire contents of the file are read into memory.
  """

  field_pos = relation.schema.field_position(path_column)
 
  return (
    row + (open(row[field_pos]).read(), )
    for row in relation(ctx)
  )

def contents_schema(relation, path_column, content_column='contents'):
  return Schema(relation.schema.fields + [dict(type='BINARY', name=content_column)])
  

def decode(ctx, relation, path_pos, mime_type, additional):
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
  
  return (
    r + tuple(s)
    for r in relation(ctx)
    for s in relation_from_path(r[path_pos], mime_type, additional=additional)
  )

def decode_resolve(func, dataset, relation, mime_type, final_schema, path_column="path"):

  path_pos = relation.schema.field_position(path_column)

  res = decode_schema(relation,  path_pos, mime_type)
  stream_schema, additional = res[0], res[1:]

  if not final_schema:
    #  let's guess... note: this is typically a slow operation
    final_schema = stream_schema

  schema =  Schema(relation.schema.fields + final_schema.fields)

  return Relation(
    None, 
    'decode', 
    schema, 
    lambda ctx: decode(ctx, relation, path_pos, mime_type, additional=additional)
  )


decode.resolve = decode_resolve

def decode_schema(relation, path_pos, mime_type):

  first = next(relation.records({}))

  path = first[path_pos]
  return schema_from_path(path, mime_type)




def files(ctx, root_dir, filename_column="path"):
  """
  Return an iterator of all filenames starting at root_dir or below
  """ 

  return (
    (join(root,f), )
    for root, dirs, files in os.walk(root_dir)
    for f in files if not f.startswith('.')
  )
 
def files_schema(root_dir, filename_column="path"):
  return Schema(
    fields = [dict(type="STRING", name=filename_column)], 
    name='files({})'.format(root_dir)
  )

def extract_path(ctx, files_relation, pattern, path_column="path"):
  """
  Extracts patterns out of file paths and urls.

  Returns a relation where the path_column is matched 
  against a reular expression expressed by the pattern
  argument.
  the resulting group info appened to the matching row.

  Example
  ['/some/path'] -> ['/some/path', 'some', 'path']
  """

  field_pos = files_relation.schema.field_position(path_column)
  regex, columns = pattern_regex(pattern)


  for row in files_relation.records(ctx):
    path = row[field_pos]
    m = regex.match(path)
    if m:
      yield row + m.groups()


def extract_path_schema(relation, pattern, path_column="path"):
  regex, columns = pattern_regex(pattern)
  schema = relation.schema

  return Schema(schema.fields + [
    dict(name=c, type='STRING')
    for c in columns    
  ], name="extract_path({})".format(pattern))


