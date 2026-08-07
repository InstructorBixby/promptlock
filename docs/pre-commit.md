# As a pre-commit hook

    repos:
      - repo: https://git.c01n31.net/c01n31pan1c/promptlock
        rev: v1.3.0
        hooks:
          - id: promptlock-verify
          - id: promptlock-check

That stanza is in `plays` and in two of the engagement repositories.
Three hooks are declared. `promptlock-fmt` is separate from the other
two and not in the example on purpose: it modifies files, and a hook
that both checks and edits is a hook I turn off the first time it
rewrites something during a rebase.

## what the hook is and is not

It is a courtesy -- it tells you about drift before you push, which is
when fixing it is a one-line amend rather than a red build.

It is **not** the gate. A hook can be skipped with `--no-verify`,
lives on whichever machine happens to have it installed, and does not
run at all on a commit made through the web UI -- and I do make
those, for one-line fixes, which is exactly when I am least careful.
The gate is the pipeline job in `docs/ci.md`, and if the hook is the
only place `verify` runs then it is not running.

## scoping

Both hooks are scoped to `prompts/` and the registry, so a commit that
cannot possibly have touched a prompt does not pay for them. Where the
prompts live somewhere else, override `files:` in that repository's
config -- it is a regular pre-commit field and the default here is
only a guess at a layout.

## the slow case

A registry of a thousand prompts takes long enough that people notice.
`--cache` exists for exactly that and is documented in
`docs/performance.md`; `verify` ignores it by design, so the hook to
put the cache on is `promptlock-check`, not the gate.

## pin the rev

`rev:` is a tag, and a canon scheme bump is a minor release, so
floating it means a tooling update here turns every prompt in a
different repository of mine into a drift report, on a morning I did
not choose. Pin it and move it deliberately, one repository at a
time.
