from typing import Any, Optional

from ..schema import Schema
from . import Adapter

NULL_SCHEMA = Schema(name="", fields=[])


class NullAdapter(Adapter):
    def has(self, relation: str) -> bool:
        if relation == "":
            return True
        else:
            return False

    def schema(self, name: str) -> Optional[Schema]:
        if name == "":
            return NULL_SCHEMA
        return None

    def table_scan(self, name: str, ctx: Any) -> Any:
        return iter(((),))
