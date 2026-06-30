# Writing this up

    promptlock export > appendix-prompts.md

Every assessment of an LLM application ends with the same table and I
have built it by hand from four sources every single time. It has four
columns -- id, owner, model tuned against, hash -- and then a list of
which suite produced which number against which hash.

## the sentence this makes possible

> The injection rate of 0.74% was measured against `support_triage` at
> `9f2c1ab4de01` (sha256, promptlock canonical form, scheme 2) using
> promptfuzz 1.3.0 with corpus hash `7c1e4f0a9b2d3e55`, against the
> staging endpoint.

Everything in that sentence except the endpoint is machine-checkable
after the fact, which is the only reason it is worth writing in that
form.

## read the staleness column before you paste

`export` marks a result measured against a hash that is no longer
pinned. That mark is the difference between a report that is true and a
report that was true. If it appears, either re-run the suite or say in
the text that the prompt has changed since the measurement -- both are
defensible, and quietly dropping the mark is not.

## what to say about the parts this cannot pin

Two, and both belong in the limitations section rather than being left
for a reader to notice:

1. **The target.** A hosted model changes with no version to pin, so
   every rate is a fact about that endpoint on that date.
2. **Assembly after loading.** Anything the application prepends,
   appends or wraps around the prompt after loading it is outside the
   template hash. If the call sites record render hashes, cite those
   too; if they do not, say that the hash covers the template only.

## what not to put in the appendix

The prompt text. It is the most sensitive configuration in the
application, the appendix is the most-forwarded part of the report, and
a hash is sufficient for everything the appendix is for. If a reader
needs the text, they can get it from the store, with whatever access
control that lives behind.
