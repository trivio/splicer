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


  try:
    dialect = sniffer.sniff(sample)
    has_header = sniffer.has_header(sample)
  except csv.Error:
    # sniffer has problems detecting single
    # column csv files
    has_header = True
    dialect = csv.excel

  reader = csv.reader(stream, dialect)


  if has_header:
    headers = reader.next()
  else:
    headers = tuple("column_%s" % col for col  in range(len(first_row)) )

  
  schema = Schema([
    dict(name=name, type="STRING")
    for name in headers
  ])

  return Relation(
    schema,
    reader
   )