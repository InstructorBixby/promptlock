# Using this with promptfuzz

The two tools answer halves of one question. promptfuzz measures how
often a payload lands against a target; promptlock says which exact
text was in the system position while it was measured. Neither is worth
much alone in a report.

    promptfuzz --url https://staging.internal/chat --pack injection-core \
        --seed 11 --repeat 10
    promptlock eval import support_triage results/run.json

That reads promptfuzz's `run.json` -- seed, corpus hash, mutator and
detector sets, plan size, versions -- counts hits from the jsonl beside
it, and appends a record bound to the hash currently pinned for
`support_triage`.

## the one thing the importer will not do

Guess the prompt id. promptfuzz points at an endpoint and has no idea
which prompt is in that endpoint's system position; inferring it from a
URL would be a guess that makes a number look attributable when it is
not. So the id is an argument, and if you point it at the wrong
endpoint you get a wrong record with your name on it rather than a
plausible-looking one with nobody's.

## the sequence that actually works

1. `promptlock lock` -- pin the text that is about to be tested.
2. Deploy that text. `promptlock verify` against the deployment.
3. Run promptfuzz against it.
4. `promptlock eval import` the run.
5. Later, `promptlock eval check` before quoting the number anywhere.

Step 2 is the one people skip, and skipping it means the pin describes
the repository rather than the thing that was measured.

## reading an imported record

`provenance.corpus_hash` is promptfuzz's own hash of the payload set. If
two records have different corpus hashes their rates are not comparable
no matter how close the numbers look -- that is promptfuzz's rule, from
its `docs/reproducing.md`, and importing a run does not soften it.
