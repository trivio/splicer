class Schema(object):
  __slots__ = {
    'fields': '-> [Field]'
  }
  def __init__(self, fields):
    self.fields = fields