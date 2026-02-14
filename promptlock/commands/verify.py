"""`promptlock verify`: the drift gate."""
from __future__ import annotations

import json
import sys

from promptlock import canon, project, report, signing


def build_report(proj: project.Project, *,
                 undeclared: bool = True) -> report.Report:
    pinned = proj.pinned()
    current = {p.id: p for p in proj.current()}
    rep = report.Report()

    for pid in sorted(set(pinned) | set(current)):
        want, have = pinned.get(pid), current.get(pid)
        if want is None:
            rep.items.append(report.Item(
                pid, report.UNPINNED,
                found_hash=have.hash, found_path=have.path,
                detail="in the registry, not in the lockfile"))
        elif have is None:
            rep.items.append(report.Item(
                pid, report.MISSING, pinned_hash=want.hash,
                pinned_path=want.path,
                detail="pinned, not in the registry"))
        elif want.hash != have.hash:
            rep.items.append(report.Item(
                pid, report.DRIFT, pinned_hash=want.hash,
                found_hash=have.hash, pinned_path=want.path,
                found_path=have.path,
                detail=f"pinned {canon.short(want.hash)}, found "
                       f"{canon.short(have.hash)}"))
        elif want.path != have.path:
            rep.items.append(report.Item(
                pid, report.MOVED, pinned_hash=want.hash,
                found_hash=have.hash, pinned_path=want.path,
                found_path=have.path,
                detail=f"pinned at {want.path}, now at {have.path} "
                       f"(same text)"))
        else:
            rep.items.append(report.Item(
                pid, report.OK, pinned_hash=want.hash,
                found_hash=have.hash, pinned_path=want.path,
                found_path=have.path,
                detail=canon.short(have.hash)))

    if undeclared:
        for source, key in proj.unregistered():
            rep.items.append(report.Item(
                f"{source}:{key}", report.UNKNOWN,
                detail="the source serves this and no [prompt.*] "
                       "table claims it"))
    return rep


def run(args) -> int:
    sig_state = ""
    if args.signature_key:
        try:
            signing.verify(args.lock, key=args.signature_key,
                           sig_path=args.signature)
            sig_state = "verified"
        except signing.SigningError as exc:
            if args.format == "json":
                print(json.dumps({"ok": False,
                                  "signature": f"failed: {exc}"},
                                 indent=1))
            else:
                print(f"promptlock: lockfile signature: {exc}",
                      file=sys.stderr)
            return 1

    proj = project.Project.open(args.registry, args.lock)
    rep = build_report(proj, undeclared=not args.no_undeclared)
    rep.signature = sig_state

    if args.format == "json":
        print(json.dumps(rep.to_json(), indent=1))
    else:
        if sig_state:
            print(f"lockfile signature verifies against "
                  f"{args.signature_key}")
        for line in rep.lines(verbose=args.verbose):
            print(line)
        if rep.failures:
            print(f"\n{len(rep.failures)} problem(s) against the "
                  f"lockfile", file=sys.stderr)
        else:
            print(f"{len(rep.items)} prompt(s) match the lockfile")
    return 1 if rep.failures else 0


def add_parser(sub) -> None:
    p = sub.add_parser("verify", help="fail if the text has drifted")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--format", choices=("human", "json"),
                   default="human")
    p.add_argument("--no-undeclared", action="store_true",
                   help="do not report prompts a source serves that "
                        "the registry does not declare")
    p.add_argument("--signature-key", default=None, metavar="KEY",
                   help="also verify the lockfile's cosign signature")
    p.add_argument("--signature", default=None,
                   help="signature path (default: <lockfile>.sig)")
    p.set_defaults(fn=run)
