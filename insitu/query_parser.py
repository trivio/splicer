import codd

from . import Field
from . import Schema
from . import relational_ops

def parse_select(statement, dataset, relations):
  schema_reader = codd.parse(statement, root_exp=select_core_exp)
  return schema_reader(dataset, relations)


def select_core_exp(tokens):
  columns = []
  while tokens:
    columns.append(result_column_exp(tokens))
    if tokens and tokens[0] == ',':
      tokens.pop(0)

  def schema(dataset, ctx):

    fs = [
      field
      for col in columns
      for field in col(dataset, ctx)
    ]

    fields, getters = zip(*fs)
    return relational_ops.ProjectOp(Schema(fields), *getters)

  return schema

def result_column_exp(tokens):
  if tokens[0] == '*':
    tokens.pop(0)
    def schema(dataset, relations): 
      return [
        (field, codd.value_exp([field.name]))
        for r in relations
        for field in r.schema.fields
      ]
    return schema
  else:
    if len(tokens) > 2 and tokens[1] =='.' and tokens[2] == '*':
      name = tokens.pop(0)
      tokens.pop(0) # '.'
      tokens.pop(0) # '*'
      # todo: need to return  lookup like 
      def table_schema(dataset, ctx):
        return dataset.get_relation(name).schema.fields
      return table_schema
    else:
      name = alias = tokens[0]
      value = codd.value_exp(tokens)
      if tokens and tokens[0].lower == 'as':
        tokens.pop(0)
        alias = tokens.pop(0)

      def field(dataset, relations):
        """
        Searches the relations for the given field name returning it if found.
        Raises a KeyError if the field was not found or ValueError if the
        name is ambigous (more than 1 relation has the same name)
        """
        fields = [
          (field, value)
          for r in relations
          for field in r.fields
          if field.name == name
        ]
        field_count = len(fields)
        if field_count == 1:
          return fields
        elif field_count == 0:
          raise KeyError("No field named {}".format(name))
        else:
          raise ValueError("Field '{}' is ambigous.".format(name))

      return field 
