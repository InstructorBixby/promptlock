"""`promptlock status`: the table somebody actually asks for.

Who owns this prompt, what was it tuned against, is it pinned, has
anything measured it, and is that measurement still about this text.
All of it exists already in four different places; this is the one
command that reads like an answer.
"""
from __future__ import annotations

import json
import sys

from promptlock import evals, lockfile, project, staleness


def rows(proj: project.Project) -> list[dict]:
    try:
        pinned = proj.pinned()
    except lockfile.LockError:
        pinned = {}
    log = evals.EvalLog(proj.store.root / "evals.jsonl")
    latest = log.latest()
    states = {(s.prompt, s.suite): s
              for s in staleness.assess(pinned, latest)}

    out = []
    for entry in proj.registry:
        pin = pinned.get(entry.id)
        suites = sorted(s for p, s in latest if p == entry.id)
        worst = ""
        if suites:
            kinds = {states[(entry.id, s)].state for s in suites}
            worst = (staleness.STALE if staleness.STALE in kinds
                     else staleness.CURRENT)
        out.append({
            "id": entry.id,
            "owner": entry.owner or "-",
            "tuned_against": entry.tuned_against or "-",
            "locator": entry.locator,
            "pinned": pin.hash[7:19] if pin else "-",
            "variables": list(entry.variables),
            "suites": suites,
            "results": worst or "none",
        })
    return out


def run(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    version = proj.lockfile_version()
    if version is not None and version != lockfile.CURRENT_VERSION:
        print(f"note: lockfile is version {version}; `promptlock lock` "
              f"will write version {lockfile.CURRENT_VERSION}",
              file=sys.stderr)
    data = rows(proj)
    if args.json:
        print(json.dumps(data, indent=1))
        return 0
    width = max([len(r["id"]) for r in data] + [2])
    print(f"{'id':{width}}  {'owner':12} {'pinned':12} "
          f"{'tuned against':22} results")
    for r in data:
        print(f"{r['id']:{width}}  {r['owner']:12} {r['pinned']:12} "
              f"{r['tuned_against']:22} {r['results']}")
    unowned = [r["id"] for r in data if r["owner"] == "-"]
    unmeasured = [r["id"] for r in data if r["results"] == "none"]
    if unowned:
        print(f"\nno owner: {', '.join(unowned)}")
    if unmeasured:
        print(f"no eval result: {', '.join(unmeasured)}")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("status", help="what is pinned, owned, measured")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=run)
