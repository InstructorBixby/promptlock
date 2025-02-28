# Design notes

## hashing the bytes is not good enough

I started with sha256 of the file. Within an hour of pointing it at a
real repo I had three prompts whose hash changed without the prompt
changing:

- an editor stripped a trailing space from the end of line 4
- someone's editor added a final newline the file did not have
- a file came back from a round trip through a web form with a BOM on it

None of those three change what the model is shown in any way I can
measure, and all three change the hash. A hash that moves for reasons
nobody cares about is a hash people learn to ignore, and then the gate
built on it is decoration.

So there has to be a *canonical form*, and the canonical form is where
all the judgement lives. Every rule in it is a claim that some
difference does not matter, and every one of those claims is wrong for
somebody. The ones I am confident about:

- UTF-8, decode strictly, strip a leading BOM
- trailing whitespace at the end of a line is not content
- exactly one trailing newline

The ones I am not:

- **line endings.** My instinct is to normalise CRLF to LF. But a
  prompt is a string handed to a tokenizer, and the tokenizer sees the
  carriage returns. If I normalise them away I am asserting that CRLF
  and LF produce identical model behaviour and I have not measured
  that.
- **Unicode normalisation.** Same argument, more sharply: NFC changes
  codepoints, and a prompt that deliberately contains a combining
  character is a prompt I would be silently rewriting.

Starting with line endings as content and no normalisation. Both are
recorded in the canon scheme so that reversing either one is a visible,
dated event rather than a hash that mysteriously moved.
