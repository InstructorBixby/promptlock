"""Where a prompt's text comes from.

The first real deployment I pointed this at kept its prompts in a
database table, edited through an admin page, which is both completely
reasonable and the exact situation that most needs a drift gate: there
is no commit, no review and no diff anywhere in that path.

So the registry declares a source, a source resolves a key to text, and
everything downstream -- canonicalisation, pinning, diffing, eval
binding -- is unchanged. A source does one thing and must do it with no
side effects: `get(key) -> str`.

Out-of-tree sources register under the `promptlock.sources` entry-point
group; see docs/sources.md.
"""
from __future__ import annotations

from importlib.metadata import entry_points

from promptlock.sources.base import MissingPrompt, Source, SourceError
from promptlock.sources.files import FileSource
from promptlock.sources.sqlite import SqliteSource

BUILTIN = {"file": FileSource, "sqlite": SqliteSource}

ENTRY_POINT_GROUP = "promptlock.sources"


def discovered() -> dict:
    out = dict(BUILTIN)
    for ep in entry_points(group=ENTRY_POINT_GROUP):
        if ep.name in BUILTIN:
            # A plugin shadowing a builtin would change what a pin
            # means depending on what is installed.
            raise SourceError(
                f"plugin {ep.value!r} would shadow the builtin source "
                f"{ep.name!r}")
        out[ep.name] = ep.load()
    return out


def build(kind: str, config: dict) -> Source:
    table = discovered()
    if kind not in table:
        known = ", ".join(sorted(table))
        raise SourceError(
            f"unknown source kind {kind!r}; known: {known}")
    return table[kind](**config)


__all__ = ["Source", "SourceError", "MissingPrompt", "FileSource",
           "SqliteSource", "BUILTIN", "ENTRY_POINT_GROUP",
           "discovered", "build"]
