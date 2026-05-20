# Verifying against a running service

    promptlock verify --deployed https://svc.internal/_promptlock \
        --header "Authorization: Bearer $TOKEN"

This is the check that says something about the system. `promptlock
verify` on its own compares the lockfile to a git checkout, which
catches a developer forgetting to re-pin and catches nothing at all
about production.

## what the application has to expose

    GET /_promptlock
    {"canon_scheme": 2,
     "prompts": {"support_triage": "sha256:9f2c1ab4de01..."}}

and the implementation is:

    from promptlock import canon

    def promptlock_report():
        return {"canon_scheme": canon.SCHEME,
                "prompts": {pid: canon.digest(text)
                            for pid, text in LOADED_PROMPTS.items()}}

Hashes, not text. The service never has to show its prompts to the CI
runner, which removes the objection that otherwise kills this endpoint
in review. Protect it anyway -- a prompt hash is a fingerprint, and an
attacker who can enumerate your prompt hashes can tell when you changed
one and can confirm a guess at the text.

## the thing to get right

The hash must be computed over the text the process **has loaded**, not
over the file it read at startup and not over the template it is about
to render. A service that re-reads the file to answer this endpoint is
reporting the file, which is the thing you already checked, and it will
happily report a hash that matches while running something else from
memory.

## scheme mismatch

If the deployment reports a different `canon_scheme`, `verify` exits 2
rather than reporting drift on everything -- it means the running
service has an older promptlock in it, which is a deployment problem
and not a prompt problem. Reporting it as forty drifted prompts would
send somebody to look at the wrong thing.

## what this still does not prove

That the loaded text is the text being sent. Anything that
post-processes a prompt after loading it -- a prefix, a per-tenant
preamble, a safety string appended by a wrapper -- is outside the hash.
`render`-side hashing is the handle on that, and it has to be done at
the call site because only the call site knows what it assembled.
