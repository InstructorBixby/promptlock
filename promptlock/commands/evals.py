"""`promptlock eval record|list|check`."""
from __future__ import annotations

import json
import sys

from promptlock import evals, project, staleness


def _log(proj: project.Project) -> evals.EvalLog:
    return evals.EvalLog(proj.store.root / "evals.jsonl")


def run_record(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    pinned = proj.pinned()
    if args.id not in pinned:
        print(f"promptlock: {args.id} is not in the lockfile; run "
              f"`promptlock lock` first", file=sys.stderr)
        return 2
    metrics = json.loads(args.metrics) if args.metrics else {}
    rec = evals.Record(
        prompt=args.id, prompt_hash=pinned[args.id].hash,
        suite=args.suite, tool=args.tool or "", metrics=metrics,
        notes=args.notes or "")
    _log(proj).append(rec)
    print(f"recorded {args.suite} for {args.id} "
          f"@ {rec.prompt_hash[7:19]}")
    return 0


def run_list(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    records = _log(proj).all()
    if args.json:
        print(json.dumps([json.loads(r.to_json()) for r in records],
                         indent=1))
        return 0
    for r in records:
        rate = r.metrics.get("rate")
        shown = "" if rate is None else f"  rate={rate}"
        print(f"{r.recorded}  {r.prompt:24} {r.suite:28} "
              f"{r.prompt_hash[7:19]}{shown}")
    return 0


def run_check(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    states = staleness.assess(proj.pinned(), _log(proj).latest(),
                              suites=args.suite or ())
    bad = 0
    for st in states:
        if st.state == staleness.CURRENT and not args.verbose:
            continue
        print(st)
        if st.state == staleness.STALE:
            bad += 1
        elif st.state == staleness.MISSING and args.require_results:
            bad += 1
    if bad:
        print(f"\n{bad} result(s) no longer describe the pinned text",
              file=sys.stderr)
        return 1
    print(f"{len(states)} binding(s) checked")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("eval", help="bind eval results to prompt hashes")
    esub = p.add_subparsers(dest="eval_cmd", required=True)

    q = esub.add_parser("record", help="record a result for a prompt")
    q.add_argument("id")
    q.add_argument("--suite", required=True)
    q.add_argument("--tool", default="")
    q.add_argument("--metrics", help="JSON object of measurements")
    q.add_argument("--notes", default="")
    q.set_defaults(fn=run_record)

    q = esub.add_parser("list", help="list recorded results")
    q.add_argument("--json", action="store_true")
    q.set_defaults(fn=run_list)

    q = esub.add_parser("check", help="are the results still current")
    q.add_argument("--suite", action="append",
                   help="require a result for this suite")
    q.add_argument("--require-results", action="store_true",
                   help="treat a prompt with no result as a failure")
    q.add_argument("-v", "--verbose", action="store_true")
    q.set_defaults(fn=run_check)
