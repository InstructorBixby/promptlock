"""`promptlock lock` and `promptlock check`."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from promptlock import canon, check, lockfile, project, registry


def _scheme(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(
            "canon_scheme")
    except json.JSONDecodeError:
        return None


def run_lock(args) -> int:
    lock_path = Path(args.lock)
    was_scheme = _scheme(lock_path)
    if was_scheme is not None and was_scheme != canon.SCHEME:
        print(f"promptlock: {lock_path} was written under canon scheme "
              f"{was_scheme}, this is scheme {canon.SCHEME}. Run "
              f"`promptlock migrate` -- a scheme bump changes every "
              f"hash and should be its own commit.", file=sys.stderr)
        return 2

    proj = project.Project.open(args.registry, args.lock,
                                cache=args.cache)
    was_version = proj.lockfile_version()
    pins = proj.lock()
    if was_version is not None and was_version != lockfile.CURRENT_VERSION:
        # Not a scheme bump: no hash changes, so this is safe to do as
        # a side effect. Saying so matters anyway, because the diff
        # renames a field on every line and a reviewer deserves to know
        # which of the two kinds of churn they are looking at.
        print(f"note: upgraded the lockfile from version "
              f"{was_version} to {lockfile.CURRENT_VERSION}. No hash "
              f"changed; `path` is now `locator`.", file=sys.stderr)
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
