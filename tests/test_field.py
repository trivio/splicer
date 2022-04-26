# test_schema_interpreter.py

from splicer.field import Field


def test_to_dict():

    assert Field(name="x", type="STRING").to_dict() == dict(
        name="x", type="STRING", mode="NULLABLE", fields=[]
    )
