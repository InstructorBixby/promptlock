# Canonical form

Scheme 1:

| rule | claim it makes |
|---|---|
| decode UTF-8 strictly | a prompt that is not valid UTF-8 is a bug, not a prompt |
| strip a leading BOM | a BOM is a transport artefact |
| strip trailing spaces and tabs per line | invisible, almost never intended |
| exactly one trailing newline | whether a file ends with a newline is an editor setting |
| line endings left alone | *not* claimed to be equivalent -- see below |
| no Unicode normalisation | *not* claimed to be equivalent -- see below |

## the two I did not do

**Line endings.** The obvious move is to fold CRLF to LF. I have not,
because the prompt is a string handed to a tokenizer and the tokenizer
sees the carriage returns; folding them asserts an equivalence I have
not measured. The cost of this decision is that a repository checked out
with CRLF translation produces different hashes, which is a real
operational hazard -- set `* text eol=lf` in `.gitattributes` for the
prompt directory and the hazard goes away.

**Unicode normalisation.** NFC would make `e` + combining acute equal to
the precomposed character, which is almost always what a human means.
But a prompt that deliberately contains a decomposed sequence -- and
prompts written to probe a model's text handling do -- would be
rewritten under me. If this ever changes it will store the raw text and
normalise only for comparison, never the other way round.

Both decisions are reversible, and reversing either is a scheme bump: a
lockfile records `canon_scheme`, and `promptlock verify` refuses to
compare hashes across schemes rather than reporting drift that is really
a tooling change.

## what canonicalisation cannot fix

A trailing space at the very end of a prompt, immediately before the
model's turn, is a real tokenisation decision in some chat templates and
scheme 1 destroys it. I have not found a rule that keeps it without also
keeping the three accidental kinds of trailing whitespace, so the
compromise is that `lock` says out loud that it stripped something.
