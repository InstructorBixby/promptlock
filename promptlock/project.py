"""Ties the registry, the lockfile and the store together.

One place for "load the registry, hash everything, compare it to the
lockfile", so that `verify`, `diff` and the eval commands cannot
disagree about what a pin means.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from promptlock import canon, lockfile, registry, store
from promptlock.cache import HashCache


@dataclass
class Project:
    registry: registry.Registry
    lock_path: Path
    store: store.Store
    cache: HashCache | None = None

    @classmethod
    def open(cls, registry_path="promptlock.toml",
             lock_path="promptlock.lock", store_root=None,
             cache: bool = False) -> "Project":
        reg = registry.load(registry_path)
        root = Path(store_root) if store_root else reg.root / ".promptlock"
        return cls(registry=reg, lock_path=Path(lock_path),
                   store=store.Store(root),
                   cache=HashCache(root / "cache" / "hashes.json",
                                   enabled=cache))

    def _digest(self, entry) -> tuple[str, str]:
        """(digest, text). Text is "" when the cache answered."""
        if entry.source or self.cache is None:
            text = self.registry.read(entry)
            return canon.digest(text), text
        path = self.registry.root / entry.path
        hit = self.cache.get(path)
        if hit:
            return hit, ""
        text = self.registry.read(entry)
        digest = canon.digest(text)
        self.cache.put(path, digest)
        return digest, text

    def current(self) -> list[lockfile.Pin]:
        pins = []
        for entry in self.registry:
            digest, _ = self._digest(entry)
            pins.append(lockfile.Pin(
                id=entry.id, path=entry.locator, hash=digest,
                owner=entry.owner, tuned_against=entry.tuned_against,
                variables=tuple(entry.variables),
                optional=tuple(entry.optional)))
        if self.cache is not None:
            self.cache.flush()
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

    def unregistered(self) -> list[tuple[str, str]]:
        """Keys a source can serve that no [prompt.*] table claims.

        A prompt in production that nobody declared is the other half
        of the drift problem and it is invisible from the registry
        side. Only reported for sources that can enumerate.
        """
        claimed = {(e.source, e.key) for e in self.registry
                   if e.source}
        out = []
        for name, src in sorted(self.registry.sources.items()):
            for key in src.keys():
                if (name, key) not in claimed:
                    out.append((name, key))
        return out
