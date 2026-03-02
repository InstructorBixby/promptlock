# promptlock

A content-addressed registry for prompts and templates, and a gate
that fails when the prompt text in a deployment stops matching the
text that was reviewed and tested.

No runtime dependencies.

## the problem

A system prompt is production-critical configuration. It decides what
an application will and will not do, it is the thing an attacker is
trying to talk past, and it is usually a triple-quoted string somebody
edited on a Friday. I keep finding this on engagements and I keep
finding it in my own repositories. Two consequences:

1. **An eval number is meaningless without the prompt text.** "Our
   injection rate is 0.7%" is a fact about a specific string. If you
   cannot produce that string byte for byte, you do not have a result.
2. **Nobody notices drift.** The prompt in the repository and the prompt
   in the running service diverge quietly, and when anyone finally looks,
   the text that was tested has not been deployed in months.

Both are fixed by the same boring thing: a canonical serialisation, a
hash, and a lockfile.

## how I run this

    uv pip install -e ".[dev]"     # here
    pipx install ./dist/promptlock-*.whl   # anywhere else

`docs/install.md` for why the pin matters in a gate.

## quickstart

    $ mkdir -p prompts && cat > prompts/triage.md <<'EOF'
    Classify the ticket below as billing, access, bug or other.
    Reply as JSON with the keys "category" and "reason".

    Ticket:
    {{ticket_body}}
    EOF

    $ cat > promptlock.toml <<'EOF'
    [prompt.triage]
    path = "prompts/triage.md"
    owner = "platform"
    tuned_against = "gpt-4o-mini"
    variables = ["ticket_body"]
    EOF

    $ promptlock lock
    locked 1 prompt(s) -> promptlock.lock

    $ promptlock verify
    1 prompt(s) match the lockfile

## a worked example: the whole point, in six commands

Change one word in the prompt and the gate notices:

    $ promptlock verify
    DRIFT    triage: pinned 9f2c1ab4de01, found 4e81b0c37a52
    1 problem(s) against the lockfile
    $ echo $?
    1

    $ promptlock diff triage
    triage: 9f2c1ab4de01 -> 4e81b0c37a52
    substantive: +1 word(s), -1 word(s). Any eval result bound to the
    old hash is now historical.

    Classify the ticket below as billing, access, [-bug-][+defect+] or
    other. Reply as JSON with the keys "category" and "reason". Ticket:
    {{ticket_body}}

Reflow the same prompt instead, changing no words, and `diff` reports
`whitespace only` -- the hash moved, the instruction did not. That
distinction is what the command exists for.

Now bind a measurement to the text that produced it:

    $ promptfuzz --url https://staging.internal/chat --pack injection-core \
        --seed 11 --repeat 10
    $ promptlock eval import triage results/run.json
    imported promptfuzz:injection-core for triage @ 4e81b0c37a52, rate=0.0074

    $ promptlock eval check
    4 binding(s) checked

Edit the prompt again and that same command says `stale`, which is the
difference between a report that is true and a report that was true.

## what it does

| | |
|---|---|
| canonical hash | `docs/canon.md` -- and the two decisions that got reversed |
| drift gate | `promptlock verify`, exit 1, the core of the thing |
| template variables | `docs/templates.md` -- missing *and* unknown are errors |
| three hashes | `docs/hashes.md` -- template, variables, rendered output |
| semantic diff | `docs/diff.md` -- whitespace-only is its own outcome |
| eval binding | `docs/evals.md`, `docs/promptfuzz.md` |
| non-file prompts | `docs/sources.md` -- a database is the case that needs this most |
| tamper-evidence | `docs/signing.md` -- and what it does not prove |
| CI | `docs/ci.md` |

## exit codes

| code | meaning |
|---|---|
| 0 | everything matched |
| 1 | drift, a failed check, a bad signature, a stale eval binding |
| 2 | usage or configuration error |

## limitations

Read this before concluding the gate covers something. It does not
cover all of it, and the gaps are where I have been bitten.

- **The hash covers the template, not the request.** Anything the
  application prepends, appends or wraps around the prompt after loading
  it is outside the template hash. Render-side hashing is the handle on
  that and it has to be called from the call site, because only the call
  site knows what it assembled.
- **It cannot pin the model.** A hosted endpoint changes under you with
  no version to pin, so an eval rate is a fact about that endpoint on
  that date. Pinning the prompt removes one of two uncontrolled
  variables.
- **`verify` on a checkout says nothing about production.** For that you
  need `--deployed` and four lines of application code. Without it the
  gate is a statement about git.
- **A hand-edited lockfile is believed.** `verify` asks whether the
  text matches the pin, so re-pinning a modified prompt satisfies it.
  Review is the control, and here review is me reading my own diff;
  signing helps only where the lockfile travels without the
  repository.
- **Canonicalisation is a set of claims, and claims can be wrong.** A
  trailing space immediately before the model's turn is destroyed by
  every scheme so far, and that space is a real tokenisation decision in
  some chat templates.
- **"Whitespace only" is a claim about words, not a promise about
  behaviour.** Moving a paragraph break can change what a model does. It
  is simply far less likely to than changing a word.
- **A source that cannot enumerate loses a check.** Undeclared live
  prompts are invisible unless the source can list its keys.
- **No multimodal anything.** Text prompts. An image in a prompt is out
  of scope and pretending otherwise would be worse than saying so.

## why I did not just use the thing that exists

I looked first. Notes, so I stop re-opening this every time the
registry feels like overhead:

| | what it is | why it was not enough |
|---|---|---|
| git alone | history and review of prompt files | no canonical hash, no name a result can bind to, nothing for prompts in a database, and `git status` is clean on a box that has not deployed in a month. `docs/why-not-git.md` is the long version and it concedes a lot. |
| a prompt-management SaaS | hosted registry, versioning, often an editor and an eval runner | an account, a network dependency and a vendor holding system prompts that are not mine to hand over. For the engagements this gets used on, that is the end of the conversation before the features matter. |
| LLM framework prompt templates | templating plus loader, inside a framework | a framework's templates are not a gate: nothing fails a build. No canonical form either, so whitespace moves the identity. I use both -- this does not render anything at runtime. |
| config management (a prompt as a YAML key) | versioned, reviewed, deployed with everything else | genuinely fine, and much better than a string in a function. It still cannot tell me whether a change mattered, and it has no concept of an eval result being about one key. |
| an eval harness's own run metadata | records the prompt alongside the result | good, and tool-specific. The prompt outlives the harness and there is more than one harness. `eval import` is the seam rather than a replacement. |

If prompts are files in a reviewed repository, most of this is already
there. What is left is the canonical hash, the gate against a running
deployment, and being able to say which exact text produced a number
-- and that last one is the whole reason I wrote it.

## what it is not

Not a prompt framework. It does not call a model, manage conversations,
chain anything, or have an opinion about what a good prompt looks like.

Not a safety test. `promptfuzz` measures whether a payload lands; this
says which text was in front of it while that was measured. Neither is
worth much alone in a report.

Not a template language. `{{name}}`, an escape, and nothing else. A
conditional in a prompt is an unreviewed branch in production, invisible
in the text that got reviewed.
