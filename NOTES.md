# Design notes

## hashing the bytes is not good enough

I started with sha256 of the file. Within an hour of pointing it at a
real repo I had three prompts whose hash changed without the prompt
changing: a stripped trailing space, an added final newline, a BOM from
a round trip through a web form. None of those change what the model is
shown in any way I can measure. A hash that moves for reasons nobody
cares about is a hash people learn to ignore, and then the gate built on
it is decoration.

So there is a canonical form, and the canonical form is where all the
judgement lives. `docs/canon.md` has the rules and the two I declined to
make.

## placeholder syntax

`{{name}}`, not `{name}`.

`str.format` is the obvious choice and it is wrong here for one reason:
prompts are full of single braces. Every prompt I have that asks for
JSON output contains a literal `{` and a literal `}`, usually in an
example, and `str.format` raises on all of them. The workaround is
doubling every brace in the prompt text, which means the text in the
file is not the text the model sees, which defeats the entire point of
hashing the file.

So: `{{name}}` is a placeholder, a single brace is literal text, and
anything else is left alone. The cost is that a prompt which itself
contains `{{` -- a prompt teaching a model to emit templates, say --
needs an escape. That is a smaller and rarer problem than JSON.

## what is deliberately not here

No conditionals, no loops, no filters, no includes. A template language
is a programming language, a programming language in a prompt is an
unreviewed branch in production, and the branch is invisible in the
prompt text that got reviewed. If a prompt needs two shapes it is two
prompts with two ids and two hashes.
