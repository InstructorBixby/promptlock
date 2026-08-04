# promptlock

A content-addressed registry for prompts and templates, and a CI gate
that fails when the prompt text in a deployment stops matching the text
that was reviewed and tested.

```
promptlock lock        # registry + text -> promptlock.lock
promptlock verify      # exit 1 on drift
```

## start here

- **[Install](install.md)** -- one line, no runtime dependencies.
- **[CI](ci.md)** -- the two jobs, and why they answer different
  questions.
- **[Canonical form](canon.md)** -- what difference counts as a change,
  and the two decisions in there that got reversed.

## the three things worth reading even if you never install it

1. **[Three hashes](hashes.md).** A template hash answers "did the
   prompt change". It does not answer "did what the model saw change",
   and those come apart the moment a variable is involved.
2. **[Binding an eval result](evals.md).** An injection rate is a fact
   about a specific string. If you cannot produce that string byte for
   byte, you have an anecdote.
3. **[Unicode](unicode.md).** Normalise to compare, store raw. This
   project learned that by shipping it the other way round and silently
   rewriting a prompt.

## what this is not

Not a prompt framework, not a safety test, not a template language.
The README's limitations section is the honest list, and the notes
next to it say where something else would have been the better
answer.
