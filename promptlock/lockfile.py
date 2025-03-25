"""`promptlock.lock`: generated, checked in, never hand-edited.

JSON rather than TOML because this file gets hashed and signed, and
canonical JSON is a solved problem whereas canonical TOML is not. The
serialisation is pinned hard: sorted keys, one-space indent, LF
endings, exactly one trailing newline. Writing it with the platform
line ending would make the file -- and therefore any signature over it
-- differ between a Linux runner and a Windows laptop.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from promptlock import canon


class LockError(Exception):
    pass


@dataclass
class Pin:
    id: str
    path: str
    hash: str
    owner: str = ""
    tuned_against: str = ""
    variables: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()

    def to_json(self) -> dict:
        out = {"id": self.id, "path": self.path, "hash": self.hash}
        if self.owner:
            out["owner"] = self.owner
        if self.tuned_against:
            out["tuned_against"] = self.tuned_against
        if self.variables:
            out["variables"] = list(self.variables)
        if self.optional:
            out["optional"] = list(self.optional)
        return out


def dumps(pins: list[Pin]) -> str:
    doc = {
        "lockfile_version": 1,
        "canon_scheme": canon.SCHEME,
        "prompts": [p.to_json()
                    for p in sorted(pins, key=lambda p: p.id)],
    }
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def write(path: str | Path, pins: list[Pin]) -> Path:
    p = Path(path)
    p.write_text(dumps(pins), encoding="utf-8", newline="\n")
    return p


def loads(text: str) -> list[Pin]:
    doc = json.loads(text)
    if doc.get("lockfile_version") != 1:
        raise LockError(
            f"lockfile_version {doc.get('lockfile_version')!r} is not "
            f"one this version understands")
    if doc.get("canon_scheme") != canon.SCHEME:
        raise LockError(
            f"lockfile was written under canon scheme "
            f"{doc.get('canon_scheme')!r}, this is scheme "
            f"{canon.SCHEME}; hashes are not comparable")
    out = []
    for row in doc.get("prompts", []):
        out.append(Pin(
            id=row["id"], path=row["path"], hash=row["hash"],
            owner=row.get("owner", ""),
            tuned_against=row.get("tuned_against", ""),
            variables=tuple(row.get("variables", ())),
            optional=tuple(row.get("optional", ())),
        ))
    return out


def read(path: str | Path) -> list[Pin]:
    p = Path(path)
    if not p.exists():
        raise LockError(f"no lockfile at {p}")
    return loads(p.read_text(encoding="utf-8"))
