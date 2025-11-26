"""The registry: `promptlock.toml`, hand-edited, checked in.

One table per prompt. The path (or source key) is where the text
lives; everything else is the metadata that makes a hash mean something
to a human six months later -- who owns it, what it was tuned against,
what variables it expects.

Sources are declared once in `[source.<name>]` and referenced by name,
so moving a prompt out of the filesystem and into a database changes
two lines and nothing downstream.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from promptlock import sources


class RegistryError(Exception):
    pass


@dataclass
class Entry:
    id: str
    path: str = ""
    source: str = ""
    key: str = ""
    owner: str = ""
    tuned_against: str = ""
    variables: list[str] = field(default_factory=list)
    optional: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def locator(self) -> str:
        """What goes in the lockfile's `path` field."""
        if self.source:
            return f"{self.source}:{self.key}"
        return self.path


@dataclass
class Registry:
    root: Path
    entries: dict[str, Entry]
    sources: dict = field(default_factory=dict)

    def __iter__(self):
        return iter(sorted(self.entries.values(), key=lambda e: e.id))

    def read(self, entry: Entry) -> str:
        if entry.source:
            src = self.sources[entry.source]
            try:
                return src.get(entry.key)
            except sources.SourceError as exc:
                raise RegistryError(f"{entry.id}: {exc}") from exc
        p = self.root / entry.path
        if not p.exists():
            raise RegistryError(f"{entry.id}: {entry.path} does not exist")
        return p.read_text(encoding="utf-8")


_ALLOWED = {"path", "source", "key", "owner", "tuned_against",
            "variables", "optional", "notes"}


def load(path: str | Path) -> Registry:
    p = Path(path)
    if not p.exists():
        raise RegistryError(f"no registry at {p}")
    data = tomllib.loads(p.read_text(encoding="utf-8"))

    declared = {}
    for name, body in (data.get("source") or {}).items():
        body = dict(body)
        kind = body.pop("kind", None)
        if not kind:
            raise RegistryError(f"source {name}: no kind")
        if "path" in body and kind != "file":
            body["path"] = str((p.parent / body["path"]).resolve())
        try:
            declared[name] = sources.build(kind, body)
        except (sources.SourceError, TypeError) as exc:
            raise RegistryError(f"source {name}: {exc}") from exc

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
        entry = Entry(id=pid, **body)
        if entry.source and entry.path:
            raise RegistryError(
                f"{pid}: has both path and source; pick one")
        if entry.source:
            if entry.source not in declared:
                raise RegistryError(
                    f"{pid}: no [source.{entry.source}] declared")
            if not entry.key:
                raise RegistryError(
                    f"{pid}: source {entry.source} needs a key")
        elif not entry.path:
            raise RegistryError(f"{pid}: no path and no source")
        entries[pid] = entry
    return Registry(root=p.parent, entries=entries, sources=declared)
