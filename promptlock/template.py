"""Placeholder parsing.

`{{name}}` is a placeholder. A single brace is literal text, because
prompts are full of single braces and a prompt that has to be escaped
before it can be hashed is not the prompt the model sees.

Deliberately not a template language: no conditionals, no loops, no
filters. See NOTES.md.
"""
from __future__ import annotations

import re

NAME = r"[A-Za-z_][A-Za-z0-9_]*"
TOKEN_RE = re.compile(r"\{\{\s*(?P<name>" + NAME + r")\s*\}\}")


class TemplateError(Exception):
    pass


class MissingVariable(TemplateError):
    pass


class UnknownVariable(TemplateError):
    pass


def variables(text: str) -> list[str]:
    """Placeholder names, in first-appearance order, deduplicated."""
    seen = []
    for m in TOKEN_RE.finditer(text):
        name = m.group("name")
        if name not in seen:
            seen.append(name)
    return seen


def render(text: str, values: dict) -> str:
    """Substitute, refusing anything ambiguous.

    Missing and unknown are both errors. The silent-empty-string
    default is the single most expensive convenience in this space: a
    prompt rendered with an empty `{{policy}}` is a prompt with no
    policy in it, the request succeeds, the model answers, and nothing
    anywhere says a word.
    """
    required = variables(text)
    missing = [v for v in required if v not in values]
    if missing:
        raise MissingVariable(
            "no value for " + ", ".join(sorted(missing)))
    unknown = [k for k in values if k not in required]
    if unknown:
        raise UnknownVariable(
            "template has no placeholder for " + ", ".join(sorted(unknown)))
    return TOKEN_RE.sub(lambda m: str(values[m.group("name")]), text)
