# Three hashes

| hash | over | answers |
|---|---|---|
| template | the canonical prompt text | did the reviewed text change |
| variables | the canonicalised bindings | did the inputs change |
| render | the canonical rendered output | did what the model saw change |

The lockfile pins the template hash, because that is the artefact a
human reviewed and the only one that exists before runtime. The other
two exist for attribution.

## why the template hash is not enough

A template hash is a fact about a file. The model is handed a rendered
string. Those diverge the moment a variable is involved, and the
divergence is where the interesting failures live:

- A retrieval step is re-tuned from three chunks to ten. Template hash
  unchanged. The model's input is now four times longer, the
  instructions are further from the end of the context, and the
  injection rate measured last month is no longer a fact about this
  system.
- A `{{policy}}` variable is fed from a config file that someone
  emptied. Template hash unchanged. The prompt now has no policy in it.
- A `{{tools}}` block is generated from a tool registry that gained a
  tool. Template hash unchanged, and the thing the prompt is describing
  has changed.

None of those are prompt edits and all of them are changes to the
prompt. A gate that only watches the template is a gate that watches the
half nobody edits.

## what to store with an eval result

All three. The template hash makes the result attributable to reviewed
text; the render hash makes it reproducible; the variables hash tells
you which of the two moved when they disagree. Storing only the render
hash looks tidier and loses the ability to say *why* a number stopped
being comparable.

## what not to do with the render hash

Do not gate on it. The render hash of anything with a retrieved variable
in it is different on every request, by design. It is an attribution
key, not an invariant.
