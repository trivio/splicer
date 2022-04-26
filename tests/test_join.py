from sys import getsizeof

import pytest

from splicer import Schema
from splicer.ast import And, EqOp, NumberConst, Var

from splicer.compilers.join import (  # type: ignore  # isort:skip
    buffered,
    hash_join,
    join_keys,
    join_keys_expr,
    nested_block_join,
    record_size,
)

SCHEMA_1 = Schema(name="t1", fields=[dict(name="x", type="INTEGER")])


def t1(ctx=None):
    return iter(((1,), (2,)))


SCHEMA_2 = Schema(
    name="t2", fields=[dict(name="y", type="INTEGER"), dict(name="z", type="INTEGER")]
)


def t2(ctx=None):
    return iter(((1, 0), (1, 1), (3, 1)))


def test_record_size():
    t = (1, 2, "blah")
    assert record_size(t) == getsizeof(t) + getsizeof(t[0]) + getsizeof(
        t[1]
    ) + getsizeof(t[2])


def test_buffering():
    t = (1, 2, "blah")
    sz = record_size(t)

    l = (t,) * 10

    assert len(list(buffered(l, sz))) == 10

    assert len(list(buffered(l, sz * 2))) == 5

    assert len(list(buffered(l, sz * 10))) == 1


def test_nested_block_join():
    r = (
        (1,),
        (2,),
        (3,),
    )

    s = (
        ("a",),
        ("b",),
        ("c",),
    )

    j = tuple(
        nested_block_join(
            lambda ctx: iter(r), lambda ctx: iter(s), lambda r, ctx: True, {}
        )
    )

    assert j == (
        (1, "a"),
        (2, "a"),
        (3, "a"),
        (1, "b"),
        (2, "b"),
        (3, "b"),
        (1, "c"),
        (2, "c"),
        (3, "c"),
    )


def test_join_key_expr():

    simple_op = EqOp(Var("t1.x"), Var("t2.y"))
    ((left_key, right_key),) = join_keys_expr(SCHEMA_1, SCHEMA_2, simple_op)

    ctx = None
    assert left_key((1,), ctx) == 1

    assert right_key((1, 0), ctx) == 1

    simple_op = EqOp(Var("t2.y"), Var("t1.x"))
    ((left_key, right_key),) = join_keys_expr(SCHEMA_1, SCHEMA_2, simple_op)

    ctx = None
    assert left_key((1,), ctx) == 1

    assert right_key((1, 0), ctx) == 1

    simple_op = EqOp(Var("t1.x"), NumberConst(1))

    with pytest.raises(ValueError):
        join_keys_expr(SCHEMA_1, SCHEMA_2, simple_op)


def test_join_keys():

    simple_op = EqOp(Var("t1.x"), Var("t2.y"))

    left_key, right_key = join_keys(SCHEMA_1, SCHEMA_2, simple_op)

    ctx = None
    assert left_key((1,), ctx) == (1,)

    assert right_key((1, 0), ctx) == (1,)

    multi_key = And(
        EqOp(Var("t1.x"), Var("t2.y")),
        EqOp(Var("t1.x"), Var("t2.z")),
    )

    left_key, right_key = join_keys(SCHEMA_1, SCHEMA_2, multi_key)

    assert left_key((1,), ctx) == (1, 1)

    assert right_key((1, 0), ctx) == (1, 0)


def test_hash_join():

    simple_op = EqOp(Var("t1.x"), Var("t2.y"))
    ctx = {}

    comparison = join_keys(SCHEMA_1, SCHEMA_2, simple_op)
    j = tuple(hash_join(False, t1, t2, comparison, ctx))

    assert j == (
        (1, 1, 0),
        (1, 1, 1),
    )

    multi_key = And(
        EqOp(Var("t1.x"), Var("t2.y")),
        EqOp(Var("t1.x"), Var("t2.z")),
    )

    comparison = join_keys(SCHEMA_1, SCHEMA_2, multi_key)
    j = tuple(hash_join(False, t1, t2, comparison, ctx))

    assert j == ((1, 1, 1),)
