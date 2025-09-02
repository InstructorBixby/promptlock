# Diffing a prompt

    promptlock diff support_triage                   # pin -> working copy
    promptlock diff support_triage --from 9f2c1ab4de01 --to pinned
    promptlock diff support_triage --to ../other/prompts/triage.md

A ref is `pinned`, `working`, a full `sha256:...` digest, a twelve-hex
short digest of something in the lockfile, or a path.

## three outcomes, not two

| outcome | meaning | what to do |
|---|---|---|
| identical | canonically the same text | nothing; the hash is stable |
| whitespace only | the hash moved, the words did not | re-pin, keep the eval results |
| substantive | words changed | re-pin, and the old eval results are historical |

The middle row is the one that justifies this command existing. A
whitespace-only change still changes the hash -- it must, the hash is
over text -- and a reviewer who cannot tell that case apart from a real
edit either re-runs a day of evals for a reflowed paragraph or, much
worse, learns to wave hash changes through.

"Whitespace only" is a claim about the word sequence, not a promise
about the model. Moving a paragraph break can change behaviour; it is
just far less likely to than changing a word, and the report says which
you are looking at rather than deciding for you.

## why word level

Prompts are wrapped prose. Inserting one word reflows the paragraph and
a line diff reports four changed lines, which buries the one word that
matters. Word level with adjacent runs merged puts the actual edit on
screen.

## where the old text comes from

`.promptlock/objects`, not git. The lockfile outlives the branch, a
prompt can come from a database rather than a file, and a report written
months later needs the text that produced a number whatever happened to
the repository in between.
