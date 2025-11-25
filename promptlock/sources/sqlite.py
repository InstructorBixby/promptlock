"""Prompts in a SQLite table.

The config is a query rather than a table and column name, because
every schema I have met puts the prompt somewhere slightly different --
a versions table where the live row is the one with `active = 1`, a
JSON blob, a join through a tenant table. A query the operator writes
covers all of those and keeps the schema knowledge out of here.

The query takes one named parameter, `:key`, and must return one row
whose first column is the text. Opened read-only: this is a gate, and a
gate that can write to the thing it is auditing is a worse gate.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from promptlock.sources.base import MissingPrompt, Source, SourceError


class SqliteSource(Source):
    kind = "sqlite"

    def __init__(self, path: str | Path, query: str,
                 keys_query: str | None = None):
        self.path = Path(path)
        self.query = query
        self.keys_query = keys_query
        if ":key" not in query:
            raise SourceError(
                "query must take a :key parameter, e.g. "
                "'select body from prompts where name = :key'")

    def _connect(self) -> sqlite3.Connection:
        if not self.path.exists():
            raise SourceError(f"no database at {self.path}")
        uri = f"file:{self.path}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def get(self, key: str) -> str:
        with self._connect() as con:
            rows = con.execute(self.query, {"key": key}).fetchall()
        if not rows:
            raise MissingPrompt(f"{key!r} is not in {self.path}")
        if len(rows) > 1:
            # Two live rows for one id is a data problem, and picking
            # one of them would hide it behind a pin that looks fine.
            raise SourceError(
                f"{key!r} matched {len(rows)} rows in {self.path}; the "
                f"query must identify exactly one")
        value = rows[0][0]
        if not isinstance(value, str):
            raise SourceError(
                f"{key!r} is {type(value).__name__}, not text")
        return value

    def keys(self) -> list[str]:
        if not self.keys_query:
            return []
        with self._connect() as con:
            return sorted(str(r[0]) for r in
                          con.execute(self.keys_query).fetchall())

    def describe(self) -> str:
        return f"sqlite({self.path})"
