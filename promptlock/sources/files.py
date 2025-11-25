"""Prompts as files on disk. The default, and the only one with no
configuration beyond a root directory."""
from __future__ import annotations

from pathlib import Path

from promptlock.sources.base import MissingPrompt, Source


class FileSource(Source):
    kind = "file"

    def __init__(self, root: str | Path = "."):
        self.root = Path(root)

    def get(self, key: str) -> str:
        p = self.root / key
        if not p.exists():
            raise MissingPrompt(f"{p} does not exist")
        return p.read_text(encoding="utf-8")

    def keys(self) -> list[str]:
        return sorted(
            str(p.relative_to(self.root))
            for p in self.root.rglob("*")
            if p.is_file() and p.suffix in (".md", ".txt", ".prompt"))

    def describe(self) -> str:
        return f"file({self.root})"
