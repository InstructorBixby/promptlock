"""The registry: `promptlock.toml`, hand-edited, checked in.

One table per prompt. The path is where the text lives; everything
else is the metadata that makes a hash mean something to a human six
months later -- who owns it, what it was tuned against, what variables
it expects.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


class RegistryError(Exception):
    pass


@dataclass
class Entry:
    id: str
    path: str
    owner: str = ""
    tuned_against: str = ""
    variables: list[str] = field(default_factory=list)
    optional: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Registry:
    root: Path
    entries: dict[str, Entry]

    def __iter__(self):
        return iter(sorted(self.entries.values(), key=lambda e: e.id))

    def read(self, entry: Entry) -> str:
        p = self.root / entry.path
        if not p.exists():
            raise RegistryError(f"{entry.id}: {entry.path} does not exist")
        return p.read_text(encoding="utf-8")


_ALLOWED = {"path", "owner", "tuned_against", "variables", "optional",
            "notes"}


def load(path: str | Path) -> Registry:
    p = Path(path)
    if not p.exists():
        raise RegistryError(f"no registry at {p}")
    data = tomllib.loads(p.read_text(encoding="utf-8"))
    prompts = data.get("prompt") or {}
    if not prompts:
        raise RegistryError(f"{p} declares no [prompt.*] tables")
    entries = {}
    for pid, body in prompts.items():
        unknown = set(body) - _ALLOWED
        if unknown:
            # A typo in a key is otherwise a silently-ignored
            # declaration, which is the worst outcome for a file whose
            # whole job is to be the declaration.
            raise RegistryError(
                f"{pid}: unknown key(s) {sorted(unknown)}")
        if "path" not in body:
            raise RegistryError(f"{pid}: no path")
        entries[pid] = Entry(id=pid, **body)
    return Registry(root=p.parent, entries=entries)
