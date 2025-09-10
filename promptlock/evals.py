"""Append-only store of eval results bound to prompt hashes.

A result is a historical fact. The store never rewrites or deletes one;
a result whose prompt has since changed becomes *stale*, which is a
thing to report rather than a thing to clean up.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class EvalError(Exception):
    pass


@dataclass
class Record:
    prompt: str
    prompt_hash: str
    suite: str
    tool: str = ""
    tool_version: str = ""
    render_hash: str | None = None
    metrics: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)
    notes: str = ""
    recorded: str = ""

    def __post_init__(self):
        if not self.recorded:
            self.recorded = datetime.now(timezone.utc).isoformat(
                timespec="seconds")

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True,
                          ensure_ascii=False)


def parse(line: str) -> Record:
    doc = json.loads(line)
    known = {f for f in Record.__dataclass_fields__}
    unknown = set(doc) - known
    if unknown:
        # Forward compatibility is the point of jsonl, but silently
        # dropping a field a newer version wrote would make a round
        # trip lossy, and the file is append-only so a round trip is
        # never needed. Report instead.
        raise EvalError(f"unknown field(s) {sorted(unknown)} in record")
    return Record(**doc)


class EvalLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, rec: Record) -> Record:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(rec.to_json() + "\n")
        return rec

    def all(self) -> list[Record]:
        if not self.path.exists():
            return []
        out = []
        for n, line in enumerate(
                self.path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(parse(line))
            except (json.JSONDecodeError, EvalError) as exc:
                raise EvalError(f"{self.path}:{n}: {exc}") from exc
        return out

    def latest(self) -> dict:
        """Most recent record per (prompt, suite)."""
        out: dict = {}
        for rec in self.all():
            out[(rec.prompt, rec.suite)] = rec
        return out
