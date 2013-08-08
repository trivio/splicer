from sys import getsizeof

B=1
K=1024
M=K**2

def record_size(record):
  # size of outer tuple
  sz = getsizeof(record)

  # size of the individual element
  # note repeating attribites aren't summed yet. To
  # do that it would be best to pass in the schema and
  # compile an efficient summer

  return sz + sum(map(getsizeof, record))

def buffered(relation, max_size):
  block = []
  bytes = 0
  for row in relation:
    block.append(row)
    bytes += record_size(row)
    if bytes >= max_size:
      yield block
      block = []
      bytes = 0

  if block:
    yield block


def nested_block_join(r,s, comparison, ctx):
  buffer_size = ctx.get('sort_buffer_size', 10*M) / 2


  for r_block in buffered(r, buffer_size):
    for s_block in buffered(s, buffer_size):
      for s_row in s_block:
        for r_row in r_block:
          row = r_row + s_row
          if comparison(row, ctx):
            yield row
