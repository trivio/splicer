from __future__ import absolute_import

import csv
from itertools import chain

from .. import Schema, Relation
from . import decodes


@decodes('text/csv')
def csv_decoder(stream):
  sample = stream.read(1024)
  stream.seek(0)
  sniffer = csv.Sniffer()

  dialect = sniffer.sniff(sample)
  reader = csv.reader(stream, dialect)

  first_row = reader.next()

  if sniffer.has_header(sample):
    headers = first_row
  else:
    headers = tuple("column_%s" % col for col  in range(len(first_row)) )
    reader = chain((first_row,), reader)

  
  schema = Schema([
    dict(name=name, type="STRING")
    for name in headers
  ])

  return Relation(
    schema,
    reader
   )