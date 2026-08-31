"""`promptlock.lock`: generated, checked in, never hand-edited.

JSON rather than TOML because this file gets hashed and signed, and
canonical JSON is a solved problem whereas canonical TOML is not. The
serialisation is pinned hard: sorted keys, one-space indent, LF
endings, exactly one trailing newline. Writing it with the platform
line ending would make the file -- and therefore any signature over it
-- differ between a Linux runner and a Windows laptop.

## versions

This file is committed in four repositories of mine -- `plays` has
one, two engagement repos have one, and so does this -- reviewed in
their diffs and in one case signed. Changing its shape means a
migration across all of them on the same afternoon, so it has a
version and the reader accepts every version that has ever been
written. The cost of that is one `row.get` on the read side. The cost
of the alternative is four repositories whose gate fails until I get
to them.

v1: `path`, which was a filesystem path.
v2: `locator`, which is a path for a file-backed prompt and
    `<source>:<key>` for everything else, plus `raw_sha256` and
    `generated_by`.

`path` was already carrying a locator in practice by the time sources
existed, which made a field called `path` contain `db:support_triage`.
v2 renames it. A v1 file is read with `path` mapped onto `locator` and
nothing lost; `lock` writes v2 and says so once.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from promptlock import canon

CURRENT_VERSION = 2
READABLE_VERSIONS = (1, 2)


class LockError(Exception):
    pass


@dataclass
class Pin:
    id: str
    locator: str
    hash: str
    owner: str = ""
    tuned_against: str = ""
    variables: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    raw_sha256: str = ""

    @property
    def path(self) -> str:
        """Deprecated alias for `locator`.

        Kept because my own code reads `pin.path`: the reporting glue,
        the `plays` wrapper, and a scratch script I will not find
        until it breaks. Removed in 2.0, per docs/stability.md.
        """
        return self.locator

    def to_json(self) -> dict:
        out: dict = {"id": self.id, "locator": self.locator,
                     "hash": self.hash}
        if self.raw_sha256:
            out["raw_sha256"] = self.raw_sha256
        if self.owner:
            out["owner"] = self.owner
        if self.tuned_against:
            out["tuned_against"] = self.tuned_against
        if self.variables:
            out["variables"] = list(self.variables)
        if self.optional:
            out["optional"] = list(self.optional)
        return out


def raw_digest(text: str) -> str:
    """sha256 of the exact bytes, not the canonical form.

    Two canonically-equal texts share a `hash` and differ here, which
    is the only way a reviewer can tell "the same prompt" from "the
    same prompt, retyped on a different operating system".
    """
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def dumps(pins: list[Pin], *, generated_by: str = "") -> str:
    doc = {
        "lockfile_version": CURRENT_VERSION,
        "canon_scheme": canon.SCHEME,
        "prompts": [p.to_json()
                    for p in sorted(pins, key=lambda p: p.id)],
    }
    if generated_by:
        doc["generated_by"] = generated_by
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def write(path: str | Path, pins: list[Pin], *,
          generated_by: str = "") -> Path:
    p = Path(path)
    p.write_text(dumps(pins, generated_by=generated_by),
                 encoding="utf-8", newline="\n")
    return p


def version_of(text: str) -> int | None:
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        return None
    v = doc.get("lockfile_version")
    return v if isinstance(v, int) else None


def loads(text: str) -> list[Pin]:
    doc = json.loads(text)
    version = doc.get("lockfile_version")
    if version not in READABLE_VERSIONS:
        readable = ", ".join(str(v) for v in READABLE_VERSIONS)
        raise LockError(
            f"lockfile_version {version!r} is not one this version "
            f"understands (readable: {readable})")
    if doc.get("canon_scheme") != canon.SCHEME:
        raise LockError(
            f"lockfile was written under canon scheme "
            f"{doc.get('canon_scheme')!r}, this is scheme "
            f"{canon.SCHEME}; hashes are not comparable")
    out = []
    for row in doc.get("prompts", []):
        # v1 called it `path`. Accept both forever on the read side;
        # the writer has emitted `locator` since v2.
        locator = row.get("locator", row.get("path", ""))
        out.append(Pin(
            id=row["id"], locator=locator, hash=row["hash"],
            owner=row.get("owner", ""),
            tuned_against=row.get("tuned_against", ""),
            variables=tuple(row.get("variables", ())),
            optional=tuple(row.get("optional", ())),
            raw_sha256=row.get("raw_sha256", ""),
        ))
    return out


def read(path: str | Path) -> list[Pin]:
    p = Path(path)
    if not p.exists():
        raise LockError(f"no lockfile at {p}")
    return loads(p.read_text(encoding="utf-8"))
