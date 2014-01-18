"""
Functions useable in the from clause
"""

from ..relation import Relation
from ..schema import Schema

def init(dataset):
  dataset.add_function("flatten", flatten, flatten_schema)


def flatten(relation, path):

  schema = relation.schema
  field = schema[path]


  if field.mode != "REPEATED" and not field.type=="RECORD":
    raise ValueError("Can not flatten non-repeating field {}".format(path))

  field_pos = schema.field_position(path)

  def flatten_repeated_scalar(row):

    for value in row[field_pos]:
      new_row = list(row)
      new_row[field_pos] = value 

      yield new_row

  def flatten_single_record(row):
    value  = row[field_pos]
    if value:
      new_row = list(row)
      values = [value.get(f.name) for f in field.fields]
      new_row[field_pos:field_pos+1] = values
      yield new_row

  def flatten_repeated_record(row):
    col = row[field_pos]
    if col:
      for value in row[field_pos]:
        new_row = list(row)
        values = [value.get(f.name) for f in field.fields]

        new_row[field_pos:field_pos+1] = values
        yield new_row


  if field.type == 'RECORD':
    if field.mode == "REPEATED":
      flatten_row = flatten_repeated_record
    else:
      flatten_row = flatten_single_record

  else:
    flatten_row = flatten_repeated_scalar

  #TODO: remove the need to wrap the results in a relation
  return Relation(
    flatten_schema(schema, path), 
    (
      new_row
      for row in relation
      for new_row in flatten_row(row)
    )
  )

def flatten_schema(schema, path):
  field = schema[path]
  new_fields = schema.fields[:]
  field_pos = schema.field_position(path)

  if field.type == 'RECORD':
    ffields = [
      f.new(name="{}_{}".format(field.name, f.name)) 
      for f in field.fields
    ]
  else:
    ffields = [field.new(mode="NULLABLE")]

  # replace the repated field with the flatten one
  new_fields[field_pos:field_pos+1] = ffields 

  return Schema(new_fields)


