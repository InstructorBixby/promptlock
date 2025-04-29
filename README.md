# promptlock

A content-addressed registry for prompts, and a CI gate that fails when
the prompt text in a deployment stops matching the text that was
reviewed and tested.

## why

A system prompt is production-critical configuration. It decides what
an application will and will not do, it is the thing an attacker is
trying to talk past, and it is usually a triple-quoted string somebody
edited on a Friday. I keep finding this on engagements and I keep
finding it in my own repositories. Two concrete consequences:

1. **An eval number is meaningless without the prompt text.** "Our
   injection rate is 0.7%" is a fact about a specific string. If you
   cannot produce that string, byte for byte, you do not have a result,
   you have an anecdote.
2. **Nobody notices drift.** The prompt in the repo and the prompt in
   the running service diverge, quietly, and the next time anyone looks
   the tested text has not been deployed for months.

Both are fixed by the same boring thing: a canonical serialisation, a
hash, and a lockfile.

## use

    promptlock lock      # registry + prompt text -> promptlock.lock
    promptlock verify    # exit 1 if anything has drifted

`promptlock.toml` is hand-edited and reviewed. `promptlock.lock` is
generated and checked in, like any other lockfile.

    [prompt.support_triage]
    path = "prompts/support_triage.md"
    owner = "platform"
    tuned_against = "gpt-4o-mini"
    variables = ["customer_name", "ticket_body"]

## exit codes

| code | meaning |
|---|---|
| 0 | everything matched |
| 1 | drift, or a prompt pinned but absent, or present but unpinned |
| 2 | usage or configuration error |

## canonicalisation

A hash of the raw bytes moves when an editor strips a trailing space,
which teaches people to ignore it. So the hash is over a canonical
form, and the rules of that form are a versioned *scheme* recorded in
the lockfile -- see `docs/canon.md`. `promptlock lock` prints a note for
every difference canonicalisation threw away, so the claim "that did not
matter" is at least visible.
