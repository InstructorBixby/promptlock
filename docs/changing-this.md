# Changes I am not allowed to make casually

Written down because the tool is now load-bearing in four of my own
repositories and I am the only person who can break it.

## anything that changes a hash

A change to `promptlock/canon.py` invalidates every lockfile and every
eval binding I have. Not hypothetically: `plays` has a committed
`promptlock.lock`, two of the engagement repos have one, and the eval
log binds rates to hashes that would all become historical in one
commit.

So it is never a change. It is a canon scheme bump, with a migration,
and the scheme number, the migration command and the changelog entry
saying every hash moves are all part of the same commit. Twice now the
thing that stopped me shipping a quiet rewrite was `verify` refusing to
compare across schemes, which is the mechanism working.

Before touching it, write down the two texts -- as a hexdump, not as
rendered text -- and which way round they should hash. If I cannot
state that in one line, I do not understand the change well enough to
make it.

## template features

No conditionals, no loops, no filters, no includes, no default values.
The reasoning is in NOTES.md and it is not a matter of effort. Every
time this feels like an inconvenience the answer is a second prompt
with its own id and its own hash.

## making `verify` faster by reading less

The gate reads every byte every time. `--cache` exists and `verify`
ignores it deliberately. Make the thing around it faster.

## the dull half

    uv pip install -e ".[dev]"
    pytest -q
    ruff check .
    mypy

ruff with the configured rules, 88 columns, `mypy --strict` over
everything outside `promptlock/commands/` -- the command modules are
argparse glue and exempt.

The suite is fast and offline: nothing in it makes a network request,
and `tests/test_deployed.py` substitutes the fetch. Keep it that way.
A test suite that needs an endpoint is a test suite I will start
skipping on a bad afternoon, and then it is not a test suite.

Anything I change needs a test in the same commit. Not as a ritual:
the entire value here is that a hash means the same thing today as it
did last quarter, and the suite is the only thing holding that.
