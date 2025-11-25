"""The source interface.

Narrow on purpose. A source is a read-only lookup from a key to text;
it does not know about hashes, lockfiles, templates or variables, and
nothing downstream knows where the text came from. That is what keeps
the gate honest about a prompt in a database: the pin means the same
thing it means for a file.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class SourceError(Exception):
    pass


class MissingPrompt(SourceError):
    pass


class Source(ABC):
    #: short name used in `kind = "..."`
    kind = ""

    @abstractmethod
    def get(self, key: str) -> str:
        """Return the text for `key`, raising MissingPrompt if absent."""

    def keys(self) -> list[str]:
        """Every key this source can serve, if it can say.

        Optional: a source that cannot enumerate returns an empty list,
        and `promptlock` then cannot report a prompt that exists in the
        source but not in the registry. That is a real loss of coverage
        and worth saying out loud rather than pretending.
        """
        return []

    def describe(self) -> str:
        return self.kind or type(self).__name__
