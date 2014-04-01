from __future__ import absolute_import

import csv
from itertools import chain

from ..schema import Schema
from ..relation import Relation
from . import decodes


@decodes('text/csv')
def csv_decoder(stream):
  sample = stream.read(1024 ** 2)
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
  
  #evil hack just for tonight. Sniffer
  # gets confused if file begins with to many
  # common delimiter characters. Long term
  # solution is to allow specifying settings when adding
  # a data set
  dialect.delimiter = '\x01'
  reader = csv.reader(stream, dialect)

  first_row = next(reader)  
  if has_header:
    headers = first_row
  else:
    headers = tuple("column_%s" % col for col  in range(len(first_row)) )
    reader = chain([first_row], reader)
  
  schema = Schema([
    dict(name=name, type="STRING")
    for name in headers
  ])

  return Relation(
    schema,
    reader
   )
