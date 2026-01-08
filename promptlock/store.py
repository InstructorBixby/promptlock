"""Content-addressed store for the texts that have been pinned.

`verify` only needs a hash. `diff` needs the old *text*, and asking git
for it does not work: a prompt can come from a database row, the
lockfile outlives the branch that produced it, and a report six months
later needs the text that produced a number regardless of what happened
to the repository. So the pinned texts are kept.

Keyed by the canonical hash, storing the RAW text. Those are different
strings on purpose: the hash has to ignore the differences
canonicalisation ignores, and the store has to be able to hand back the
exact bytes that were reviewed.
"""
from __future__ import annotations

from pathlib import Path

from promptlock import canon


class StoreError(Exception):
    pass


class Store:
    def __init__(self, root: str | Path = ".promptlock") -> None:
        self.root = Path(root)

    def _path(self, digest: str) -> Path:
        algo, _, hexd = digest.partition(":")
        if algo != "sha256" or len(hexd) != 64:
            raise StoreError(f"not a digest: {digest!r}")
        if not all(c in "0123456789abcdef" for c in hexd):
            # A digest is the only thing that ever reaches this
            # function, and a digest cannot contain a path separator.
            # Checking anyway, because the lockfile is a file an
            # attacker may control and this is where that would land.
            raise StoreError(f"not a digest: {digest!r}")
        return self.root / "objects" / algo / hexd[:2] / hexd[2:]

    def put(self, text: str) -> str:
        digest = canon.digest(text)
        p = self._path(digest)
        raw = text.encode("utf-8")
        if p.exists():
            if p.read_bytes() != raw:
                # Two raw texts with one canonical hash. Legitimate --
                # that is what canonicalisation is for -- but the stored
                # copy is then not the only text this hash has meant,
                # and silently overwriting it loses that.
                raise StoreError(
                    f"{canon.short(digest)} is already stored with "
                    f"different raw bytes; canonically equal, literally "
                    f"not. Use force_put to replace it.")
            return digest
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return digest

    def force_put(self, text: str) -> str:
        digest = canon.digest(text)
        p = self._path(digest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
        return digest

    def has(self, digest: str) -> bool:
        return self._path(digest).exists()

    def get(self, digest: str) -> str:
        p = self._path(digest)
        if not p.exists():
            raise StoreError(
                f"{canon.short(digest)} is not in the store")
        return p.read_bytes().decode("utf-8")
