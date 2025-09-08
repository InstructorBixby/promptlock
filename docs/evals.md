# Binding an eval result to a prompt

The claim this exists to make possible: *this number was produced by
this exact text.*

Without it, every security number about an LLM application is an
anecdote. "We measured a 0.7% injection rate" is a fact about a string,
a target, a corpus and a date. Three of those four are usually
recorded. The string almost never is, and the string is the one the
application team keeps editing.

## the record

An append-only `.promptlock/evals.jsonl`. One object per result:

    {"recorded": "2025-07-22T15:02:11+00:00",
     "prompt": "support_triage",
     "prompt_hash": "sha256:9f2c1ab4de01...",
     "render_hash": null,
     "suite": "promptfuzz:injection-core",
     "tool": "promptfuzz", "tool_version": "1.3.0",
     "metrics": {"sends": 4200, "hits": 31, "rate": 0.00738},
     "provenance": {"seed": 11, "corpus_hash": "7c1e4f0a9b2d3e55"}}

Append-only because a result is a historical fact. When the prompt
changes, the old result does not become wrong, it becomes *about
something else*, and deleting it loses the ability to say so.

## stale means something precise

A record is **stale** when its `prompt_hash` is not the hash currently
pinned for that id. Stale is not a failure. It is a statement that the
number no longer describes the pinned text, which is exactly what you
need to know before pasting it into a report.

    promptlock eval check

exits 1 if any prompt in the registry has no current result, or if a
result is being carried forward against a prompt whose hash has moved.

## what a hash cannot bind

The target. A hosted model changes under you with no version to pin, so
a rate from six months ago is a historical fact about that endpoint on
that day. `promptfuzz`'s own `docs/reproducing.md` makes the same point
and it is worth repeating here: pinning the prompt removes one of the
two uncontrolled variables, not both. The honest form of a claim is
"against this text, on that endpoint, on that date".

## why not just put it in the eval tool

Because there is more than one eval tool, and because the prompt
outlives any of them. The binding belongs next to the thing being
measured, not inside whichever harness happened to measure it.
