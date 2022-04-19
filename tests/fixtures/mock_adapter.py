from splicer import Table
from splicer.adapters import Adapter


class MockAdapter(Adapter):
    def __init__(self):

        table = Table(
            adapter=self,
            name="bogus",
            schema=dict(
                fields=[dict(name="x", type="INTEGER"), dict(name="y", type="INTEGER")]
            ),
        )

        self._tables = {table.name: table}

    @property
    def relations(self):
        return [(name, table.schema) for name, table in self._tables.items()]

    def has(self, name):
        return name in self._tables

    def schema(self, name):
        return self._tables[name].schema

    def get_relation(self, name):
        return self._tables.get(name)
