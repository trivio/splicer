"""
Functions useable in the from clause
"""

from ..relation import Relation
from ..schema import Schema

def init(dataset):
  dataset.add_function("flatten", flatten, None)

def flatten(relation, path):

  schema = relation.schema

  field = schema[path]
  if field.mode != "REPEATED":
    raise ValueError("Can not flatten non-repeating field {}".format(path))

  field_pos = schema.field_position(path)

  def flatten_repeated_scalar(row):
    for value in row[field_pos]:
      new_row = list(row)
      new_row[field_pos] = value 

      yield new_row

  def flatten_repeated_record(row):

    for value in row[field_pos]:
      new_row = list(row)
      values = [value.get(f.name) for f in field.fields]

      new_row[field_pos:field_pos+1] = values
      yield new_row


  if field.type == 'RECORD':
    ffields = [
      f.new(name="{}_{}".format(field.name, f.name)) 
      for f in field.fields
    ]
    flatten_row = flatten_repeated_record
  else:
    ffields = [field.new(mode="NULLABLE")]
    flatten_row = flatten_repeated_scalar



  new_fields = schema.fields[:]


  # replace the repated field with the flatten one
  new_fields[field_pos:field_pos+1] = ffields 

  schema = Schema(new_fields)

  fields = schema.fields


  return Relation(
    schema, 
    (
      new_row
      for row in relation
      for new_row in flatten_row(row)
    )
  )

