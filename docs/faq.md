# FAQ

**Why does `verify` fail when I only reformatted a prompt?**

Because the hash is over text and you changed the text. Run
`promptlock diff <id>`: if it says whitespace-only, re-pin with
`promptlock lock` and keep your eval results. That is the whole purpose
of the three-outcome diff.

**Why is `render` so strict? An empty string would be fine.**

It would not. A prompt rendered with an empty `{{policy}}` is a prompt
with no policy in it; the request succeeds, the model answers, and
nothing anywhere says a word. Every permissive renderer I have met has
shipped exactly that bug at least once.

**My prompt contains `{{` and the parser complains.**

Double it: `{{{{name}}}}` renders as the literal `{{name}}`. There is no
raw-block syntax and there will not be -- see NOTES.md.

**Can a prompt have a default value for a variable?**

No. A default is a second prompt hiding inside the first, with no id and
no hash. Two shapes is two prompts.

**Does this call a model?**

No. Nothing in here makes a request except `verify --deployed`, which
does one GET against an endpoint you name, and the signing path, which
shells out to cosign.

**Why is the lockfile JSON when the registry is TOML?**

The registry is hand-edited and TOML is nicer for that. The lockfile is
generated, hashed and sometimes signed, and canonical JSON is a solved
problem whereas canonical TOML is not.

**Can I hand-edit the lockfile?**

You can, and `verify` will believe you. That is what the signing
support is for, and `docs/signing.md` is clear about how little it
proves on its own.

**The short hashes are only twelve characters.**

They are for reading aloud and pasting into a chat message. Never use
one as a lookup key; the full digest is in the lockfile.

**Does it work with prompts that are not in English?**

Yes, and the Unicode handling matters more there, so read
`docs/unicode.md`. The hash NFC-normalises and the stored text does
not, deliberately.

**Why isn't there a `promptlock test` that runs my evals?**

Because then this would be an eval harness with a registry attached,
and it would be a worse eval harness than `promptfuzz` and a worse
registry than this. `eval import` is the seam.
