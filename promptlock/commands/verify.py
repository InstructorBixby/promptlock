"""`promptlock verify`: the drift gate."""
from __future__ import annotations

import sys

from promptlock import canon, project


def run(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    pinned = proj.pinned()
    current = {p.id: p for p in proj.current()}

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
        elif want.path != have.path:
            print(f"MOVED    {pid}: pinned at {want.path}, now at "
                  f"{have.path} (same text)")
        elif args.verbose:
            print(f"ok       {pid}: {canon.short(have.hash)}")

    if not args.no_undeclared:
        for source, key in proj.unregistered():
            print(f"UNKNOWN  {source}:{key}: the source serves this "
                  f"and no [prompt.*] table claims it")
            drift += 1

    if drift:
        print(f"\n{drift} problem(s) against the lockfile",
              file=sys.stderr)
        return 1
    print(f"{len(current)} prompt(s) match the lockfile")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("verify", help="fail if the text has drifted")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--no-undeclared", action="store_true",
                   help="do not report prompts a source serves that "
                        "the registry does not declare")
    p.set_defaults(fn=run)
