"""promptlock command line.

Exit codes matter more than output here, because the only interesting
caller is CI:

  0  everything matched
  1  drift: deployed text does not match its pin
  2  usage or configuration error
"""
from __future__ import annotations

import argparse
import sys

from promptlock import canon, lockfile, registry


def _pins(reg: registry.Registry) -> list[lockfile.Pin]:
    pins = []
    for entry in reg:
        text = reg.read(entry)
        pins.append(lockfile.Pin(
            id=entry.id, path=entry.path, hash=canon.digest(text),
            owner=entry.owner, tuned_against=entry.tuned_against,
            variables=tuple(entry.variables),
            optional=tuple(entry.optional)))
    return pins


def cmd_lock(args) -> int:
    reg = registry.load(args.registry)
    pins = _pins(reg)
    lockfile.write(args.lock, pins)
    for entry in reg:
        text = reg.read(entry)
        for note in canon.lossy(text):
            print(f"{entry.id}: note: {note}", file=sys.stderr)
    print(f"locked {len(pins)} prompt(s) -> {args.lock}")
    return 0


def cmd_verify(args) -> int:
    reg = registry.load(args.registry)
    pinned = {p.id: p for p in lockfile.read(args.lock)}
    current = {p.id: p for p in _pins(reg)}

    drift = 0
    for pid in sorted(set(pinned) | set(current)):
        want, have = pinned.get(pid), current.get(pid)
        if want is None:
            print(f"UNPINNED {pid}: in the registry, not in the lockfile")
            drift += 1
        elif have is None:
            print(f"MISSING  {pid}: pinned, not in the registry")
            drift += 1
        elif want.hash != have.hash:
            print(f"DRIFT    {pid}: pinned {canon.short(want.hash)}, "
                  f"found {canon.short(have.hash)}")
            drift += 1
        elif args.verbose:
            print(f"ok       {pid}: {canon.short(have.hash)}")
    if drift:
        print(f"\n{drift} prompt(s) do not match the lockfile",
              file=sys.stderr)
        return 1
    print(f"{len(current)} prompt(s) match the lockfile")
    return 0


def cmd_hash(args) -> int:
    for path in args.paths:
        with open(path, encoding="utf-8") as fh:
            print(canon.digest(fh.read()), path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="promptlock")
    ap.add_argument("--registry", default="promptlock.toml")
    ap.add_argument("--lock", default="promptlock.lock")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("lock", help="write the lockfile from the registry")
    p.set_defaults(fn=cmd_lock)

    p = sub.add_parser("verify", help="fail if the text has drifted")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("hash", help="hash files, ignoring the registry")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_hash)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (registry.RegistryError, lockfile.LockError) as exc:
        print(f"promptlock: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
