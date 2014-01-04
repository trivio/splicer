import mimetypes
from ..schema import Schema

decoders_by_mime_type = {}

def decodes(mime_type):
  def wraps(f):
    decoders_by_mime_type[mime_type] = f
    return f
  return wraps

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

from . import csv