"""Ties the registry, the lockfile and the store together.

The CLI had grown three copies of "load the registry, hash everything,
compare it to the lockfile". One place for it, so that `verify`,
`diff` and the eval commands cannot disagree about what a pin means.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from promptlock import canon, lockfile, registry, store


@dataclass
class Project:
    registry: registry.Registry
    lock_path: Path
    store: store.Store

    @classmethod
    def open(cls, registry_path="promptlock.toml",
             lock_path="promptlock.lock", store_root=None) -> "Project":
        reg = registry.load(registry_path)
        root = Path(store_root) if store_root else reg.root / ".promptlock"
        return cls(registry=reg, lock_path=Path(lock_path),
                   store=store.Store(root))

    def current(self) -> list[lockfile.Pin]:
        pins = []
        for entry in self.registry:
            text = self.registry.read(entry)
            pins.append(lockfile.Pin(
                id=entry.id, path=entry.path, hash=canon.digest(text),
                owner=entry.owner, tuned_against=entry.tuned_against,
                variables=tuple(entry.variables),
                optional=tuple(entry.optional)))
        return pins

    def pinned(self) -> dict:
        return {p.id: p for p in lockfile.read(self.lock_path)}

    def lock(self) -> list[lockfile.Pin]:
        pins = self.current()
        for entry in self.registry:
            text = self.registry.read(entry)
            if not self.store.has(canon.digest(text)):
                self.store.put(text)
        lockfile.write(self.lock_path, pins)
        return pins

    def text_for(self, digest: str) -> str:
        return self.store.get(digest)
