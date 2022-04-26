from splicer.schema import Schema


def test_schema():
    # assert_is_instance(ast, NumberConst)

    schema = Schema(
        name="a",
        fields=[
            dict(name="y", type="STRING"),
            dict(name="x", type="STRING"),
        ],
    )

    assert schema.field_position("y") == 0
    assert schema.field_position("x") == 1
    assert schema.field_position("a.y") == 0
