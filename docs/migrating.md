# Migrating across a canon scheme

A scheme bump changes every hash in the lockfile. Three things fall out
of that, and all three are deliberate:

1. `promptlock verify` **refuses** rather than reporting drift. Forty
   prompts all showing as drifted is indistinguishable from forty
   prompts having been edited, and the correct reaction to the two is
   opposite.
2. `promptlock lock` **refuses** to overwrite a lockfile from an older
   scheme. Otherwise the first person to run any command turns a
   tooling change into an unexplained forty-line diff.
3. `promptlock migrate` is the only thing that does it, it prints the
   old and new hash of every prompt, and it has a `--dry-run`.

## the sequence

    promptlock migrate --dry-run     # read the list
    promptlock migrate               # one commit, nothing else in it
    promptlock eval check             # everything is now stale

That last line is not a problem to fix. Every eval record is bound to a
hash computed under the old scheme, so by construction none of them
match. They are still correct facts about the text they measured; what
has changed is the name of that text. Re-record against the new hashes
when the evals are next run, and until then the staleness report is
telling the truth.

## what a scheme bump is not

It is not a reason to rewrite history. The old objects stay in the
store, the old records stay in the log, and `promptlock diff` across
the boundary still works because it compares texts, not hashes.
