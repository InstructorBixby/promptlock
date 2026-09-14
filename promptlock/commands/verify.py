"""`promptlock verify`: the drift gate."""
from __future__ import annotations

import argparse
import json
import sys

from promptlock import (canon, deployed, deprecations, project, report,
                        signing)


def build_report(proj: project.Project, *,
                 undeclared: bool = True,
                 live: dict | None = None) -> report.Report:
    """Compare the lockfile against the registry, or against a service.

    `live` is id -> hash as reported by a running deployment. When it is
    given, the comparison is pin versus production rather than pin
    versus checkout, which is the one that says something about the
    system rather than about the repository.
    """
    pinned = proj.pinned()
    if live is None:
        found = {p.id: (p.hash, p.locator) for p in proj.current()}
    else:
        found = {pid: (h, "deployed") for pid, h in live.items()}
    rep = report.Report()

    for pid in sorted(set(pinned) | set(found)):
        want = pinned.get(pid)
        have = found.get(pid)
        if want is None:
            rep.items.append(report.Item(
                pid, report.UNPINNED, found_hash=have[0],
                found_locator=have[1],
                detail="running, not in the lockfile" if live
                       else "in the registry, not in the lockfile"))
        elif have is None:
            rep.items.append(report.Item(
                pid, report.MISSING, pinned_hash=want.hash,
                pinned_locator=want.locator,
                detail="pinned, not reported by the deployment" if live
                       else "pinned, not in the registry"))
        elif want.hash != have[0]:
            rep.items.append(report.Item(
                pid, report.DRIFT, pinned_hash=want.hash,
                found_hash=have[0], pinned_locator=want.locator,
                found_locator=have[1],
                detail=f"pinned {canon.short(want.hash)}, found "
                       f"{canon.short(have[0])}"))
        elif want.locator != have[1] and live is None:
            rep.items.append(report.Item(
                pid, report.MOVED, pinned_hash=want.hash,
                found_hash=have[0], pinned_locator=want.locator,
                found_locator=have[1],
                detail=f"pinned at {want.locator}, now at {have[1]} "
                       f"(same text)"))
        else:
            rep.items.append(report.Item(
                pid, report.OK, pinned_hash=want.hash,
                found_hash=have[0], pinned_locator=want.locator,
                found_locator=have[1], detail=canon.short(have[0])))

    if undeclared and live is None:
        for source, key in proj.unregistered():
            rep.items.append(report.Item(
                f"{source}:{key}", report.UNKNOWN,
                detail="the source serves this and no [prompt.*] "
                       "table claims it"))
    return rep


def run(args) -> int:
    skip_undeclared = args.skip_undeclared
    if args.no_undeclared:
        deprecations.warn_flag("--no-undeclared")
        skip_undeclared = True

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

    live = None
    if args.deployed:
        headers = {}
        for item in args.header or []:
            k, _, v = item.partition(":")
            headers[k.strip()] = v.strip()
        try:
            doc = deployed.fetch(args.deployed, headers=headers,
                                 timeout=args.timeout)
        except deployed.DeployedError as exc:
            print(f"promptlock: {exc}", file=sys.stderr)
            return 2
        if (doc["canon_scheme"] is not None
                and doc["canon_scheme"] != canon.SCHEME):
            print(f"promptlock: the deployment reports canon scheme "
                  f"{doc['canon_scheme']}, this is scheme "
                  f"{canon.SCHEME}; the hashes are not comparable",
                  file=sys.stderr)
            return 2
        live = doc["prompts"]

    proj = project.Project.open(args.registry, args.lock)
    rep = build_report(proj, undeclared=not skip_undeclared, live=live)
    rep.signature = sig_state

    if args.format == "json":
        print(json.dumps(rep.to_json(), indent=1))
    else:
        if sig_state:
            print(f"lockfile signature verifies against "
                  f"{args.signature_key}")
        if live is not None:
            print(f"against {args.deployed}")
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
    p.add_argument("--deployed", metavar="URL", default=None,
                   help="compare the pins against the hashes a running "
                        "service reports")
    p.add_argument("--header", action="append", metavar="K: V")
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--skip-undeclared", action="store_true",
                   help="do not report prompts a source serves that "
                        "the registry does not declare")
    # Deprecated spelling, hidden from --help but still honoured.
    p.add_argument("--no-undeclared", action="store_true",
                   help=argparse.SUPPRESS)
    p.add_argument("--signature-key", default=None, metavar="KEY",
                   help="also verify the lockfile's cosign signature")
    p.add_argument("--signature", default=None,
                   help="signature path (default: <lockfile>.sig)")
    p.set_defaults(fn=run)
