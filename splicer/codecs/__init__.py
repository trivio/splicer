from functools import partial
import mimetypes
from ..schema import Schema


decoders_by_mime_type = {}

def decodes(mime_type):
  def wraps(f):
    decoders_by_mime_type[mime_type] = f
    f.schema = partial(set_schema_mimetype, f)

    return f
  return wraps

def set_schema_mimetype(decoder_func, schema_infer_func):
  """
  Partial function used to make the following decorator pattern work

  @codecs.decods("text/csv")
  def csv_decoder(stream):
    # function used to decode the given stream

  @csv_decoder.schema
  def csv_schema(stream):
    # function used to infer the schema from the given stream,
    # used when the schema isn't implicitly set



  """
  decoder_func.returns = schema_infer_func
  return decoder_func

def relation_from(stream, mime_type):
  # todo guess mime_type if not provided
  decoder = decoders_by_mime_type.get(mime_type)
  if decoder:
    return decoder(stream)
  else:
    return None

def relation_from_path(path, mime_type=None, encoding=None):
  if mime_type is None or mime_type == 'auto':
    mime_type, encoding = mimetypes.guess_type(path)

  return relation_from(open(path), mime_type)


def schema_from(stream, mime_type):
  decoder = decoders_by_mime_type.get(mime_type)
  if decoder:
    return decoder.returns(stream)
  else:
    return None

def schema_from_path(path, myme_type, encoding):
  if mime_type is None or mime_type == 'auto':
    mime_type, encoding = mimetypes.guess_type(path)

  return schema_from(open(path), mime_type)

  
from . import csv