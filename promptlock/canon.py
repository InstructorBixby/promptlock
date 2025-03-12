"""Canonical serialisation of prompt text.

Everything in here is a claim that some textual difference does not
change what a model is shown. The claims are versioned as a *scheme*
number so that changing one is a dated, visible event: a hash computed
under scheme 1 and a hash computed under scheme 2 are not comparable
and the lockfile records which it used.

Scheme 1:
  - decode UTF-8 strictly, strip a leading BOM
  - strip trailing spaces and tabs from every line
  - exactly one trailing newline
  - line endings are content, NOT normalised
  - no Unicode normalisation
"""
from __future__ import annotations

import hashlib

SCHEME = 1
BOM = "\ufeff"


def canonical(text: str) -> str:
    if text.startswith(BOM):
        text = text[1:]
    lines = [ln.rstrip(" \t") for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def lossy(text: str) -> list[str]:
    """What canonicalisation threw away, in words, for a human."""
    notes = []
    if text.startswith(BOM):
        notes.append("leading byte-order mark stripped")
    body = text[1:] if text.startswith(BOM) else text
    if any(ln != ln.rstrip(" \t") for ln in body.split("\n")[:-1]):
        notes.append("trailing whitespace stripped from one or more lines")
    if body and not body.endswith("\n"):
        notes.append("final newline added")
    if body.endswith("\n\n"):
        notes.append("repeated final newlines collapsed to one")
    return notes


def digest(text: str) -> str:
    """Hash of the canonical form, prefixed with its algorithm."""
    raw = canonical(text).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def short(d: str) -> str:
    """Twelve hex characters. Long enough for a human, never compared."""
    return d.split(":", 1)[-1][:12]
