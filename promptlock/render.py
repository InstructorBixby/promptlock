"""Hashes for the three things that can change what a model is shown.

A template hash answers "did the prompt text change". It does not
answer "did what the model saw change", and those come apart as soon as
a variable is involved: a retrieval step that starts returning twice as
much text changes the model's input completely while the template hash
sits still. The eval was run against a rendered string, not a template,
so the rendered string is what has to be attributable.
"""
from __future__ import annotations

import hashlib
import json
from typing import TypedDict

from promptlock import canon, template


class Hashes(TypedDict):
    template: str
    variables: str
    render: str


def variables_hash(values: dict[str, object]) -> str:
    """Hash of the variable bindings, canonicalised per value.

    Keys sorted, values canonicalised with the same scheme as prompt
    text so a trailing space in a retrieved chunk does not move it.
    """
    doc = {k: canon.canonical(str(v)) for k, v in sorted(values.items())}
    raw = json.dumps(doc, sort_keys=True,
                     ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def render_hash(text: str, values: dict[str, object]) -> str:
    """Hash of the text the model is actually handed."""
    return canon.digest(template.render(text, values))


def hashes(text: str, values: dict[str, object]) -> Hashes:
    """All three, for a provenance record."""
    return {
        "template": canon.digest(text),
        "variables": variables_hash(values),
        "render": render_hash(text, values),
    }
