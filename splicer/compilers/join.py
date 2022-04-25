#type: ignore
from collections import defaultdict
from functools import partial
from sys import getsizeof

from ..ast import And, EqOp, Var
from .local import var_expr

B = 1
K = 1024
M = K**2
MAX_SIZE = 10 * M


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


def nested_block_join(r_op, s_op, comparison, ctx):
    buffer_size = ctx.get("sort_buffer_size", MAX_SIZE) / 2
    r = r_op(ctx)

    for r_block in buffered(r, buffer_size):
        s = s_op(ctx)
        for s_block in buffered(s, buffer_size):
            for s_row in s_block:
                for r_row in r_block:
                    row = r_row + s_row
                    if comparison(row, ctx):
                        yield row


def hash_join(left_join, l_op, r_op, comparison, ctx):
    r = r_op(ctx)
    buffer_size = ctx.get("sort_buffer_size", MAX_SIZE) / 2

    left_key, right_key = comparison

    if left_join:
        default = ((None,) * len(r_op.schema.fields),)
    else:
        default = ()

    for r_block in buffered(r, buffer_size):
        probe = defaultdict(list)
        for row in r_block:
            probe[right_key(row, ctx)].append(row)

        for l_block in buffered(l_op(ctx), buffer_size):
            for l_row in l_block:
                for r_row in probe.get(left_key(l_row, ctx), default):
                    yield l_row + r_row


def join_keys(left_schema, right_schema, op):
    """
    Given two relations that need to be joined and
    a expression, returns two functions for extracting
    keys suitable for equi joins from the relations


    """

    def key_func(funcs, row, ctx):
        return tuple(f(row, ctx) for f in funcs)

    l_key, r_key = zip(*join_keys_expr(left_schema, right_schema, op))

    return partial(key_func, l_key), partial(key_func, r_key)


def join_keys_expr(left_schema, right_schema, op):
    """
    Rerturn the function for extracting the key values from the expresion
    or  (None,None) if the operation is not an EqOp with two vars.

    All of thes following expresions

    left.x = right.y
    right.y = left.x
    x = y
    y = x
    left.x = y
    y = left.x
    right.y = x
    x = right.y

    Are equivalent and should return a list of two functions
    the first function will extract x from a row in the left relation
    and extract y from a row in the right relation.
    """

    if isinstance(op, And):
        return join_keys_expr(left_schema, right_schema, op.lhs) + join_keys_expr(
            left_schema, right_schema, op.rhs
        )

    if not isinstance(op, EqOp):
        raise ValueError("Expression is not equijoinable")

    if not (isinstance(op.lhs, Var) and isinstance(op.rhs, Var)):
        # the query rewritter should push expresions that don't
        # involve both sides of the relation down the tree
        raise ValueError("Expression is not equijoinable")

    cols = [None, None]
    for var in (op.lhs, op.rhs):
        parts = var.path.split(".")
        if len(parts) == 1:
            if left_schema.field_map.get(parts[0]):
                cols[0] = var_expr(var, left_schema, None)
            elif right_schema.field_map.get(parts[0]):
                cols[1] = var_expr(var, right_schema, None)
            else:
                raise ValueError('column "{}" does not exist'.format(var.path))
        else:
            relation_name = parts[0]
            if left_schema.name == relation_name:
                cols[0] = var_expr(Var(parts[1]), left_schema, None)
            elif right_schema.name == relation_name:
                cols[1] = var_expr(Var(parts[1]), right_schema, None)
            else:
                raise ValueError('relation "{}" does not exist'.format(parts[0]))

    return (cols,)
