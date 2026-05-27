"""Skip re-hashing a file that has not changed.

A registry of forty prompts is instant and needs none of this. The one
that prompted it had eleven hundred, in a monorepo, with the gate on a
pre-commit hook, and hashing all of them on every commit was eight
seconds of somebody's attention.

Keyed on (path, size, mtime_ns). Deliberately NOT keyed on content,
because the whole point is to avoid reading the content. That makes this
a heuristic: a file rewritten within one mtime tick, at the same size,
with different content, hashes stale. It is the same bet every build
system makes, and the two places it must not be taken are `verify` in
CI and anything that signs, so both ignore the cache.
"""
from __future__ import annotations

import json
from pathlib import Path


class HashCache:
    def __init__(self, path: str | Path, enabled: bool = True):
        self.path = Path(path)
        self.enabled = enabled
        self._data: dict = {}
        self._dirty = False
        if enabled and self.path.exists():
            try:
                self._data = json.loads(
                    self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                # A corrupt cache is not an error, it is an empty cache.
                self._data = {}

    @staticmethod
    def _key(p: Path) -> str:
        st = p.stat()
        return f"{p}|{st.st_size}|{st.st_mtime_ns}"

    def get(self, p: str | Path) -> str | None:
        if not self.enabled:
            return None
        p = Path(p)
        if not p.exists():
            return None
        return self._data.get(self._key(p))

    def put(self, p: str | Path, digest: str) -> None:
        if not self.enabled:
            return
        p = Path(p)
        if not p.exists():
            return
        self._data[self._key(p)] = digest
        self._dirty = True

    def flush(self) -> None:
        if not (self.enabled and self._dirty):
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Keep it bounded: a monorepo accumulates an entry per mtime
        # per file and the file would otherwise grow forever.
        items = list(self._data.items())[-20000:]
        self.path.write_text(
            json.dumps(dict(items), sort_keys=True),
            encoding="utf-8", newline="\n")
        self._dirty = False
