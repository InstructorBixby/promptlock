"""Deprecated spellings, in one place, with the removal version in the
table rather than in a comment somebody will not find.

The rules, from docs/stability.md, are the whole reason this module is
boring:

- the old spelling keeps working
- the warning goes to stderr, never stdout, because something parses
  stdout and a warning inside a JSON document is a breaking change
  wearing a courtesy as a disguise
- the exit code does not change; a gate that starts failing over a
  rename is a gate people switch off
"""
from __future__ import annotations

import sys

#: old -> (new, version it is removed in)
FLAGS = {
    "--no-undeclared": ("--skip-undeclared", "2.0"),
}

#: old -> (new, version it is removed in). JSON output field names.
JSON_FIELDS = {
    "pinned_path": ("pinned_locator", "2.0"),
    "found_path": ("found_locator", "2.0"),
}


def warn_flag(old: str) -> None:
    new, gone = FLAGS[old]
    print(f"promptlock: {old} is deprecated, use {new}. The old "
          f"spelling is removed in {gone}.", file=sys.stderr)


def with_aliases(doc: dict) -> dict:
    """Add the deprecated field names alongside the current ones."""
    out = dict(doc)
    for old, (new, _) in JSON_FIELDS.items():
        if new in out:
            out[old] = out[new]
    return out
