"""`promptlock lock` and `promptlock check`."""
from __future__ import annotations

import sys

from promptlock import canon, check, project, registry


def run_lock(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    pins = proj.lock()
    for entry in proj.registry:
        for note in canon.lossy(proj.registry.read(entry)):
            print(f"{entry.id}: note: {note}", file=sys.stderr)
    print(f"locked {len(pins)} prompt(s) -> {args.lock}")
    return 0


def run_check(args) -> int:
    problems = check.check(registry.load(args.registry))
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("no problems")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("lock", help="write the lockfile from the registry")
    p.set_defaults(fn=run_lock)

    p = sub.add_parser("check", help="is the registry's declaration true")
    p.set_defaults(fn=run_check)
