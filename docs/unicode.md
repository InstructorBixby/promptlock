# Unicode, and the one place this tool got it wrong

The hash NFC-normalises. The file on disk, and the object in the store,
keep exactly the codepoints the author wrote. Those are different on
purpose and the reason is a bug I shipped.

## what happened

`promptlock fmt` wrote the canonical form back to the file so the thing
in the editor would match the thing being hashed. The canonical form
includes NFC normalisation. One of the prompts in the registry was a
text-handling probe: it deliberately contained a decomposed sequence,
because the question it existed to ask was what the model does with a
base character followed by a combining mark.

`fmt` turned it into the precomposed character. Nothing drifted, nothing
failed, the hash did not change -- it could not, the hash folds exactly
that difference -- and the prompt stopped testing the thing it was
written to test. It was only noticed because the probe's results went
quiet.

That is the worst possible shape for a bug in a tool like this: a silent
edit to a production instruction, made by the tool whose entire purpose
is to make edits to production instructions visible.

## the rule now

| operation | normalises | writes to disk |
|---|---|---|
| `canon.canonical` (hash) | yes | never |
| `canon.formatted` (`fmt`) | no | yes |

Normalise to compare. Store raw. Not the other way round, ever. Where
the two disagree, `lock` and `fmt` both say so on stderr rather than
choosing for you.

## what the hash folding NFC does and does not mean

It means two canonically-equivalent texts get one hash, so a prompt
retyped on a different operating system does not read as an edit. It
does **not** mean the two texts are interchangeable in front of a model:
they are different token sequences. If that distinction is the content
of your prompt, the hash is the wrong instrument and `promptlock diff`
against the stored raw object is the right one.

## what NFC is not

NFC is not a confusable or invisible-character filter. It will not fold
a Cyrillic `a` into a Latin `a`, it will not remove a zero-width space,
and it will not touch a bidi override. A prompt can be NFC-clean and
still contain text that renders as something other than what it is.
That is a different problem with a different tool -- `glyphstop` -- and
running it over the prompt directory is worth doing; `promptlock` has no
opinion on confusables and should not acquire one.
