"""
path.py - functions for manipulation and extracting data from paths.
"""

import re


from codd import Tokens

def tokenize_pattern(pattern):
  t = Tokens(pattern)
  while not t.at_end():
    if t.current_char == '/':
      yield t.read_char()
    elif t.current_char == '{':
      yield t.read_until('}') + t.read_char()
    else:
      yield t.read_until('/{')


def regex_str(tokens):
  r = []
  for t in tokens:
    if t.startswith('{'):
      r.append('(?P<%s>[^/]*)' % t[1:-1])
    else:
      r.append(re.escape(t))
  return ''.join(r)

def pattern_regex(pattern_str):
  tokens = list(tokenize_pattern(pattern_str))
  
  return (
    re.compile(regex_str(tokens)),  # regex
    [t[1:-1] for t in tokens if t.startswith('{')] # tokennames
  )
