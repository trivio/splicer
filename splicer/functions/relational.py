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

  if field.type == 'RECORD':
    ffields = field.fields
  else:
    ffields = [field.new(mode="NULLABLE")]

  field_pos = schema.field_position(path)

  new_fields = schema.fields[:]


  # replace the repated field with the flatten one
  new_fields[field_pos:field_pos+1] = ffields 

  schema = Schema(new_fields)

  fields = schema.fields

  def flattened(row):
    for value in row[field_pos]:
      new_row = list(row)
      new_row[field_pos] = value 

      yield new_row


  return Relation(
    schema, 
    (
      new_row
      for row in relation
      for new_row in flattened(row)
    )
  )

