from __future__ import absolute_import

import csv
from itertools import chain

from ..schema import Schema
from ..field import Field
from . import decodes

SAMPLE_SIZE = (1024 ** 2) // 5

@decodes('text/csv')
def csv_decoder(stream, dialect='excel', has_header=True):

  reader = csv.reader(stream, dialect)
  if has_header:
    # skip header, we've read it already during schema
    next(reader)  

  return reader


@csv_decoder.schema
def csv_schema(stream):
  pos = stream.tell()
  sample = stream.read(SAMPLE_SIZE)
  stream.seek(pos)
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

  first_row = next(reader)  
  if has_header:
    headers = first_row
  else:
    headers = tuple("column_%s" % col for col  in range(len(first_row)) )
    reader = chain([first_row], reader)

  return Schema([
    Field(name=name, type="STRING")
    for name in headers
  ])
