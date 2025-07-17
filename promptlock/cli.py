"""promptlock command line.

Exit codes matter more than output here, because the only interesting
caller is CI:

  0  everything matched
  1  drift, or a failed check
  2  usage or configuration error
"""
from __future__ import annotations

import argparse
import json
import sys

from promptlock import (canon, check, lockfile, project, registry,
                        render, store, template)


def _open(args) -> project.Project:
    return project.Project.open(args.registry, args.lock)


def _values(args) -> dict:
    values = {}
    if args.vars:
        with open(args.vars, encoding="utf-8") as fh:
            values = json.load(fh)
    for item in args.set or []:
        k, _, v = item.partition("=")
        values[k] = v
    return values


def cmd_lock(args) -> int:
    proj = _open(args)
    pins = proj.lock()
    for entry in proj.registry:
        for note in canon.lossy(proj.registry.read(entry)):
            print(f"{entry.id}: note: {note}", file=sys.stderr)
    print(f"locked {len(pins)} prompt(s) -> {args.lock}")
    return 0


def cmd_verify(args) -> int:
    proj = _open(args)
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
        elif args.verbose:
            print(f"ok       {pid}: {canon.short(have.hash)}")
    if drift:
        print(f"\n{drift} prompt(s) do not match the lockfile",
              file=sys.stderr)
        return 1
    print(f"{len(current)} prompt(s) match the lockfile")
    return 0


def cmd_check(args) -> int:
    problems = check.check(registry.load(args.registry))
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("no problems")
    return 0


def cmd_render(args) -> int:
    reg = registry.load(args.registry)
    if args.id not in reg.entries:
        print(f"promptlock: no prompt {args.id!r}", file=sys.stderr)
        return 2
    text = reg.read(reg.entries[args.id])
    try:
        if args.hash:
            print(json.dumps(render.hashes(text, _values(args)),
                             indent=1, sort_keys=True))
        else:
            sys.stdout.write(template.render(text, _values(args)))
    except template.TemplateError as exc:
        print(f"promptlock: {args.id}: {exc}", file=sys.stderr)
        return 2
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

    p = sub.add_parser("check", help="is the registry's declaration true")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("render", help="render a prompt with variables")
    p.add_argument("id")
    p.add_argument("--vars", help="JSON file of variable values")
    p.add_argument("--set", action="append", metavar="K=V")
    p.add_argument("--hash", action="store_true",
                   help="print the template, variables and render "
                        "hashes instead of the text")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("hash", help="hash files, ignoring the registry")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_hash)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (registry.RegistryError, lockfile.LockError,
            store.StoreError) as exc:
        print(f"promptlock: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
