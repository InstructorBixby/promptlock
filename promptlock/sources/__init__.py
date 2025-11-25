"""Where a prompt's text comes from.

The first real deployment I pointed this at kept its prompts in a
database table, edited through an admin page, which is both completely
reasonable and the exact situation that most needs a drift gate: there
is no commit, no review and no diff anywhere in that path.

So the registry declares a source, a source resolves a key to text, and
everything downstream -- canonicalisation, pinning, diffing, eval
binding -- is unchanged. A source does one thing and must do it with no
side effects: `get(key) -> str`.
"""
from __future__ import annotations

from promptlock.sources.base import Source, SourceError
from promptlock.sources.files import FileSource

BUILTIN = {"file": FileSource}


def build(kind: str, config: dict) -> Source:
    if kind in BUILTIN:
        return BUILTIN[kind](**config)
    raise SourceError(f"unknown source kind {kind!r}")


__all__ = ["Source", "SourceError", "FileSource", "BUILTIN", "build"]
