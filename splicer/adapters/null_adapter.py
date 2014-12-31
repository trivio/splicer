from ..schema import Schema
from . import Adapter

NULL_SCHEMA = Schema(name="",fields=[])

class NullAdapter(Adapter):
  def has(self, relation):
    if relation == '':
      return True

  def schema(self, name):
    if name == '':
      return NULL_SCHEMA

  def table_scan(self, name, ctx):
    return iter(((),))

