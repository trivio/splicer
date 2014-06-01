from __future__ import absolute_import

import csv
from itertools import chain

from ..schema import Schema
from . import decodes


@decodes('text/csv')
def csv_decoder(stream):
  pos = stream.tell()
  sample = stream.read(1024 ** 2)
  
  #TODO do not modify stream location...
  stream.seek(pos)
  sniffer = csv.Sniffer()


  #TODO: Remove sniffing if the schema and dialect are already known
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

  return reader


@csv_decoder.schema
def csv_schema(stream):
  pos = stream.tell()
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

  reader = csv.reader(stream, dialect)

  first_row = next(reader)  
  if has_header:
    headers = first_row
  else:
    headers = tuple("column_%s" % col for col  in range(len(first_row)) )
    reader = chain([first_row], reader)
  
  return Schema([
    dict(name=name, type="STRING")
    for name in headers
  ])
