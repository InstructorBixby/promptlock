"""Canonical serialisation of prompt text.

Two operations, and keeping them apart is the point of this module.

`canonical()` produces the form that gets *hashed*. It folds every
difference this tool claims is not content, including Unicode
normalisation. It is never written to disk.

`formatted()` produces the form that gets *written* to disk by
`promptlock fmt`. It folds only the differences that are
unambiguously editor artefacts: whitespace, line endings, the BOM, the
final newline. It does not normalise, because normalising a file is
editing a production instruction.

The claims are versioned as a *scheme* number so changing one is a
dated, visible event: a hash computed under scheme 1 and a hash
computed under scheme 2 are not comparable, and the lockfile records
which it used.

Scheme 2:
  - decode UTF-8 strictly, strip a leading BOM
  - fold CRLF and lone CR to LF
  - NFC normalise (hash only)
  - strip trailing spaces and tabs from every line
  - exactly one trailing newline
"""
from __future__ import annotations

import hashlib
import unicodedata

SCHEME = 2
BOM = "\ufeff"


def _strip_bom(text: str) -> str:
    return text[1:] if text.startswith(BOM) else text


def _layout(text: str) -> str:
    """Whitespace, line endings, final newline. No codepoint changes."""
    text = _strip_bom(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip(" \t") for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def formatted(text: str) -> str:
    """Safe to write back over the author's file."""
    return _layout(text)


def canonical(text: str) -> str:
    """Hashed, never written."""
    return unicodedata.normalize("NFC", _layout(text))


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def lossy(text: str) -> list[str]:
    """What canonicalisation threw away, in words, for a human."""
    notes = []
    if text.startswith(BOM):
        notes.append("leading byte-order mark stripped")
    body = _strip_bom(text)
    if "\r" in body:
        notes.append("carriage returns folded to LF")
    if not is_nfc(body):
        notes.append(
            "text is not in NFC; the hash folds the difference, the "
            "file and the stored object keep the raw sequence "
            "(docs/unicode.md)")
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
