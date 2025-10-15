"""Canonical serialisation of prompt text.

Everything in here is a claim that some textual difference does not
change what a model is shown. The claims are versioned as a *scheme*
number so that changing one is a dated, visible event: a hash computed
under scheme 1 and a hash computed under scheme 2 are not comparable
and the lockfile records which it used.

Scheme 2:
  - decode UTF-8 strictly, strip a leading BOM
  - fold CRLF and lone CR to LF
  - NFC normalise
  - strip trailing spaces and tabs from every line
  - exactly one trailing newline

Scheme 1 did not fold line endings and did not normalise. See
docs/canon.md for why that did not survive contact with a Windows
checkout.
"""
from __future__ import annotations

import hashlib
import unicodedata

SCHEME = 2
BOM = "\ufeff"


def _strip_bom(text: str) -> str:
    return text[1:] if text.startswith(BOM) else text


def canonical(text: str) -> str:
    text = _strip_bom(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFC", text)
    lines = [ln.rstrip(" \t") for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def lossy(text: str) -> list[str]:
    """What canonicalisation threw away, in words, for a human."""
    notes = []
    if text.startswith(BOM):
        notes.append("leading byte-order mark stripped")
    body = _strip_bom(text)
    if "\r" in body:
        notes.append("carriage returns folded to LF")
    if unicodedata.normalize("NFC", body) != body:
        notes.append(
            "text is not in NFC; the hash folds the difference but the "
            "stored object keeps the raw sequence (docs/unicode.md)")
    flat = body.replace("\r\n", "\n").replace("\r", "\n")
    if any(ln != ln.rstrip(" \t") for ln in flat.split("\n")[:-1]):
        notes.append("trailing whitespace stripped from one or more lines")
    if flat and not flat.endswith("\n"):
        notes.append("final newline added")
    if flat.endswith("\n\n"):
        notes.append("repeated final newlines collapsed to one")
    return notes


def digest(text: str) -> str:
    """Hash of the canonical form, prefixed with its algorithm."""
    raw = canonical(text).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def short(d: str) -> str:
    """Twelve hex characters. Long enough for a human, never compared."""
    return d.split(":", 1)[-1][:12]
