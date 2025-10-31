"""`promptlock migrate`: re-pin a lockfile under the current scheme.

A scheme bump changes every hash in the file. That must not look like
drift, and it must not be something `lock` does quietly as a side
effect of being run -- the diff of a scheme migration is 40 changed
hashes and the reviewer needs to know that is what they are looking at.

So: `verify` refuses to compare across schemes, `lock` refuses to
overwrite a lockfile from an older scheme, and this is the one command
that does it, with the old and new hash of every prompt printed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from promptlock import canon, lockfile, project


def _scheme_of(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(
            "canon_scheme")
    except json.JSONDecodeError:
        return None


def run(args) -> int:
    lock_path = Path(args.lock)
    was = _scheme_of(lock_path)
    if was is None:
        print(f"promptlock: no readable lockfile at {lock_path}",
              file=sys.stderr)
        return 2
    if was == canon.SCHEME:
        print(f"{lock_path} is already scheme {canon.SCHEME}")
        return 0

    old_rows = {row["id"]: row["hash"] for row in json.loads(
        lock_path.read_text(encoding="utf-8")).get("prompts", [])}

    proj = project.Project.open(args.registry, args.lock)
    pins = proj.current()
    print(f"canon scheme {was} -> {canon.SCHEME}")
    moved = 0
    for pin in pins:
        old = old_rows.get(pin.id, "")
        if old != pin.hash:
            moved += 1
        print(f"  {pin.id:28} {canon.short(old) or '(new)':>12} -> "
              f"{canon.short(pin.hash)}")
    if args.dry_run:
        print(f"\n{moved} hash(es) would change; nothing written")
        return 0
    for entry in proj.registry:
        text = proj.registry.read(entry)
        if not proj.store.has(canon.digest(text)):
            proj.store.put(text)
    lockfile.write(lock_path, pins)
    print(f"\n{moved} hash(es) changed, {len(pins)} pin(s) written")
    print("Any eval record bound to an old hash is now stale by "
          "construction; `promptlock eval check` will say so.")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser(
        "migrate", help="re-pin the lockfile under the current scheme")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=run)
