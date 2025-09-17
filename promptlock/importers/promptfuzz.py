"""Read a `promptfuzz` run and turn it into an eval record.

promptfuzz writes `run.json` beside its jsonl with the seed, the corpus
hash, the mutator and detector sets, the versions and the plan size.
That is almost exactly the provenance this wants, so the importer is
mostly a field mapping -- with one deliberate refusal.

The refusal: promptfuzz measures a *target*, not a prompt. Nothing in
`run.json` says which prompt was in the system position of the thing it
was pointed at, because promptfuzz cannot know. So the prompt id is an
argument the operator supplies, and this module will not guess it from
the endpoint URL. A wrong binding is worse than no binding: it makes a
number look attributable when it is not.
"""
from __future__ import annotations

import json
from pathlib import Path

from promptlock.evals import Record


class ImportError_(Exception):
    pass


def _counts(jsonl: Path) -> tuple[int, int]:
    sends = hits = 0
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        sends += 1
        if row.get("hit"):
            hits += 1
    return sends, hits


def read(run_json: str | Path, *, prompt: str, prompt_hash: str,
         suite: str | None = None, results: str | Path | None = None
         ) -> Record:
    p = Path(run_json)
    if not p.exists():
        raise ImportError_(f"no run.json at {p}")
    meta = json.loads(p.read_text(encoding="utf-8"))
    if meta.get("tool") != "promptfuzz":
        raise ImportError_(
            f"{p} says tool={meta.get('tool')!r}, not promptfuzz")

    jsonl = Path(results) if results else p.with_name("run.jsonl")
    metrics: dict = {}
    if jsonl.exists():
        sends, hits = _counts(jsonl)
        metrics = {"sends": sends, "hits": hits}
        if sends:
            metrics["rate"] = round(hits / sends, 6)
    elif meta.get("planned_sends"):
        # The plan size is not a result. Record it as provenance and
        # leave the metrics empty rather than implying a rate.
        metrics = {}

    prov = {k: meta[k] for k in
            ("seed", "corpus", "corpus_hash", "payloads", "mutators",
             "detectors", "target", "repeat", "planned_sends",
             "started", "platform", "python")
            if k in meta}
    prov["run_json"] = str(p)
    if meta.get("warnings"):
        prov["warnings"] = list(meta["warnings"])

    return Record(
        prompt=prompt, prompt_hash=prompt_hash,
        suite=suite or f"promptfuzz:{meta.get('corpus', 'unknown')}",
        tool="promptfuzz", tool_version=meta.get("version", ""),
        metrics=metrics, provenance=prov)
