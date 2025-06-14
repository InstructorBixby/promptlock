"""Placeholder parsing.

`{{name}}` is a placeholder. `{{{{name}}}}` is the literal text
`{{name}}`. A single brace is literal, because prompts are full of
single braces and a prompt that has to be escaped before it can be
hashed is not the prompt the model sees.

Deliberately not a template language: no conditionals, no loops, no
filters. See NOTES.md.
"""
from __future__ import annotations

import re

NAME = r"[A-Za-z_][A-Za-z0-9_]*"
# The escape alternative is first so that `{{{{x}}}}` is consumed whole
# rather than being read as a placeholder wrapped in stray braces.
TOKEN_RE = re.compile(
    r"\{\{\{\{\s*(?P<literal>" + NAME + r")\s*\}\}\}\}"
    r"|\{\{\s*(?P<name>" + NAME + r")\s*\}\}")
# Anything that looks like it was meant to be a placeholder and is not
# one. Reported, never guessed at.
SUSPECT_RE = re.compile(r"\{\{(?!\{\{)[^}\n]{0,80}(?:\}\}|$)")


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
        if name and name not in seen:
            seen.append(name)
    return seen


def suspicious(text: str) -> list[str]:
    """Things shaped like a placeholder that this parser will not fill.

    A misspelled or unclosed placeholder is otherwise indistinguishable
    from prose, and ships as literal braces in front of a model.
    """
    out = []
    for m in SUSPECT_RE.finditer(text):
        if TOKEN_RE.fullmatch(m.group(0)):
            continue
        frag = m.group(0).strip()
        if frag not in out:
            out.append(frag)
    return out


def _sub(m, values):
    if m.group("literal"):
        return "{{" + m.group("literal") + "}}"
    return str(values[m.group("name")])


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
    return TOKEN_RE.sub(lambda m: _sub(m, values), text)
