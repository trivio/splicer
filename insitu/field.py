class Field(object):
  __slots__ = {
    'name': "-> string [REQUIRED]"
    'type': "-> string [REQUIRED] integer|float|string|boolean|date|datetime|time|record",
    'mode': "-> string [OPTIONAL] REQUIRED|NULLABLE|REPEATED: default NULLABLE",
    'fields': "-> list [OPTIONAL IF type = RECORD]"
  }