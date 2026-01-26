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

Now change one word in the prompt:

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

Reflow that same prompt instead and `diff` says `whitespace only`,
which is the distinction the whole command exists for.

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
| CI | `docs/ci.md` |

## exit codes

| code | meaning |
|---|---|
| 0 | everything matched |
| 1 | drift, a failed check, a stale eval binding |
| 2 | usage or configuration error |

## what it is not

Not a prompt framework. It does not call a model, manage conversations,
chain anything, or have an opinion about what a good prompt looks like.

Not a safety test. `promptfuzz` measures whether a payload lands; this
says which text was in front of it while that was measured.

Not a template language. `{{name}}`, an escape, and nothing else.
