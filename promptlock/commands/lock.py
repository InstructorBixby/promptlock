"""`promptlock lock` and `promptlock check`."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from promptlock import canon, check, project, registry


def _lockfile_scheme(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(
            "canon_scheme")
    except json.JSONDecodeError:
        return None


def run_lock(args) -> int:
    lock_path = Path(args.lock)
    was = _lockfile_scheme(lock_path)
    if was is not None and was != canon.SCHEME:
        print(f"promptlock: {lock_path} was written under canon scheme "
              f"{was}, this is scheme {canon.SCHEME}. Run "
              f"`promptlock migrate` -- a scheme bump changes every "
              f"hash and should be its own commit.", file=sys.stderr)
        return 2
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
