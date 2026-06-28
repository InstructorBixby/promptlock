"""`promptlock export`: the appendix a report needs.

Every assessment of an LLM application ends with the same table, and
every time I have built it by hand from four sources. Prompt id, owner,
the model it was tuned against, the hash of the exact text that was in
front of the tests, and which suite produced which number against which
hash.

Markdown because that is what goes into a report, JSON because
something downstream always wants it. No new facts: this is the data
from the lockfile and the eval log, arranged the way the question gets
asked.
"""
from __future__ import annotations

import json
import sys

from promptlock import evals, project, staleness


def collect(proj: project.Project) -> list[dict]:
    pinned = proj.pinned()
    latest = evals.EvalLog(proj.store.root / "evals.jsonl").latest()
    states = {(s.prompt, s.suite): s
              for s in staleness.assess(pinned, latest)}
    out = []
    for entry in proj.registry:
        pin = pinned.get(entry.id)
        results = []
        for (pid, suite), rec in sorted(latest.items()):
            if pid != entry.id:
                continue
            results.append({
                "suite": suite,
                "tool": rec.tool,
                "tool_version": rec.tool_version,
                "metrics": rec.metrics,
                "measured_against": rec.prompt_hash,
                "state": states[(pid, suite)].state,
                "recorded": rec.recorded,
            })
        out.append({
            "id": entry.id,
            "owner": entry.owner,
            "tuned_against": entry.tuned_against,
            "locator": entry.locator,
            "hash": pin.hash if pin else "",
            "variables": list(entry.variables),
            "optional": list(entry.optional),
            "results": results,
        })
    return out


def markdown(rows: list[dict], scheme: int) -> str:
    out = ["# Prompt inventory", "",
           f"Hashes are sha256 over the promptlock canonical form, "
           f"scheme {scheme}.", "",
           "| id | owner | tuned against | hash |",
           "|---|---|---|---|"]
    for r in rows:
        out.append(f"| `{r['id']}` | {r['owner'] or '-'} | "
                   f"{r['tuned_against'] or '-'} | "
                   f"`{r['hash'][7:19] or '-'}` |")
    out += ["", "## results", ""]
    any_result = False
    for r in rows:
        for res in r["results"]:
            any_result = True
            note = ("" if res["state"] == staleness.CURRENT
                    else "  **measured against a hash that is no "
                         "longer pinned**")
            metrics = ", ".join(f"{k}={v}"
                                for k, v in sorted(res["metrics"].items()))
            out.append(f"- `{r['id']}` / {res['suite']} "
                       f"({res['tool'] or 'unrecorded'}): "
                       f"{metrics or 'no metrics recorded'}, against "
                       f"`{res['measured_against'][7:19]}`.{note}")
    if not any_result:
        out.append("No eval results are bound to any of these prompts.")
    out.append("")
    return "\n".join(out)


def run(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    rows = collect(proj)
    if args.format == "json":
        print(json.dumps(rows, indent=1))
        return 0
    from promptlock import canon
    sys.stdout.write(markdown(rows, canon.SCHEME))
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("export", help="prompt inventory for a report")
    p.add_argument("--format", choices=("markdown", "json"),
                   default="markdown")
    p.set_defaults(fn=run)
