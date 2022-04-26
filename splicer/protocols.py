from __future__ import annotations

from typing import Literal

FieldType = Literal[
    "INTEGER", "FLOAT", "STRING", "BOOLEAN", "DATE", "DATETIME", "TIME", "RECORD"
]
Mode = Literal["REQUIRED", "NULLABLE", "REPEATED"]
