# Canonical form

## scheme 2

| rule | claim it makes |
|---|---|
| decode UTF-8 strictly | a prompt that is not valid UTF-8 is a bug, not a prompt |
| strip a leading BOM | a BOM is a transport artefact |
| fold CRLF and lone CR to LF | line endings are transport, not content |
| NFC normalise | canonically-equivalent sequences are the same text |
| strip trailing spaces and tabs per line | invisible, almost never intended |
| exactly one trailing newline | whether a file ends with a newline is an editor setting |

## scheme 1, and why it changed

Scheme 1 deliberately did *not* fold line endings or normalise Unicode,
on the grounds that both change codepoints and the tokenizer sees
codepoints. The argument was sound and the decision was wrong, for a
reason that has nothing to do with tokenizers.

I cloned `plays` on the Windows VM I keep for client documents, with
line-ending translation on, and every prompt came out CRLF at
checkout. Not edited -- checked out. `promptlock verify` reported
drift on all of them, and I spent twenty minutes reading the hashing
code before I thought to look at the file.

`.gitattributes` fixes it, and this repository has had one since the
beginning, and that is not a defence: a gate whose correctness depends
on every checkout being configured right is a gate that is wrong on
the machine I am sitting at and right in the test suite. The rule has
to hold with no cooperation, including mine.

Having conceded the principle for line endings I cannot keep it for
Unicode either. Two sequences that are canonically equivalent render
identically, no reviewer can tell them apart, and the one that is in the
file depends on which operating system typed it. Folding both.

What I give up: the ability to distinguish CRLF from LF, and precomposed
from decomposed, at the level of the hash. For a prompt that is
*deliberately* probing a model's text handling that distinction is the
whole content of the prompt. The handling for that case is that the
stored object keeps the raw text -- `diff` and the eval records show you
exactly what was reviewed -- and the hash folds. See `docs/unicode.md`.

## scheme bumps

A lockfile records `canon_scheme`. `verify` refuses to compare hashes
across schemes rather than reporting drift that is really a tooling
change, and `promptlock migrate` rewrites a lockfile under the current
scheme so the change is one reviewable commit.

## what canonicalisation still cannot fix

A trailing space at the very end of a prompt, immediately before the
model's turn, is a real tokenisation decision in some chat templates and
every scheme so far destroys it. I have not found a rule that keeps it
without also keeping the three accidental kinds of trailing whitespace,
so the compromise is that `lock` says out loud that it stripped
something.
