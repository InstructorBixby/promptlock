"""Turn word spans into something readable in a terminal.

Inline markers rather than colour by default, because the first place
this gets pasted is a merge request comment or a note to myself, and
neither keeps the escape codes.
"""
from __future__ import annotations

import textwrap

from promptlock import diff

MARKERS = {"add": ("[+", "+]"), "del": ("[-", "-]")}


def inline(a: str, b: str, width: int = 78) -> str:
    parts = []
    for span in diff.word_spans(a, b):
        if span.op == "same":
            parts.append(span.text)
        else:
            lo, hi = MARKERS[span.op]
            parts.append(f"{lo}{span.text}{hi}")
    body = " ".join(p for p in parts if p)
    return "\n".join(textwrap.wrap(body, width=width,
                                    break_long_words=False)) + "\n"


def summary(a: str, b: str) -> str:
    kind = diff.classify(a, b)
    added, removed = diff.changed_word_count(a, b)
    if kind == diff.IDENTICAL:
        return "identical (canonically)"
    if kind == diff.WHITESPACE_ONLY:
        return ("whitespace only: the hash changed, the words did not. "
                "A re-pin is enough; a re-run of the evals is not "
                "obviously needed.")
    return (f"substantive: +{added} word(s), -{removed} word(s). "
            f"Any eval result bound to the old hash is now historical.")
