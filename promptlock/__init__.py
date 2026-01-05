"""promptlock: a content-addressed registry and drift gate for prompts.

The names re-exported here are the supported API. Anything reached by
importing a submodule directly may move in a minor release -- see
docs/stability.md.
"""
from __future__ import annotations

from promptlock.canon import (SCHEME, canonical, digest, formatted,
                              is_nfc, lossy, short)
from promptlock.evals import EvalLog, Record
from promptlock.lockfile import Pin
from promptlock.registry import Entry, Registry, RegistryError
from promptlock.render import hashes, render_hash, variables_hash
from promptlock.sources.base import MissingPrompt, Source, SourceError
from promptlock.template import (MissingVariable, TemplateError,
                                 UnknownVariable, render, variables)

__version__ = "0.6.0"

__all__ = [
    "SCHEME",
    "EvalLog",
    "Entry",
    "MissingPrompt",
    "MissingVariable",
    "Pin",
    "Record",
    "Registry",
    "RegistryError",
    "Source",
    "SourceError",
    "TemplateError",
    "UnknownVariable",
    "__version__",
    "canonical",
    "digest",
    "formatted",
    "hashes",
    "is_nfc",
    "lossy",
    "render",
    "render_hash",
    "short",
    "variables",
    "variables_hash",
]
