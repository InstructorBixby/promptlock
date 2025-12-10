# Sources

A prompt does not have to be a file. The first real deployment I pointed
this at kept its prompts in a database table edited through an admin
page -- which is a perfectly reasonable design and also the situation
that most needs a drift gate, because there is no commit, no review and
no diff anywhere in that path.

## declaring one

    [source.db]
    kind = "sqlite"
    path = "var/prompts.db"
    query = "select body from prompts where name = :key and active = 1"
    keys_query = "select name from prompts where active = 1"

    [prompt.support_triage]
    source = "db"
    key = "support_triage"
    owner = "platform"
    variables = ["customer_name", "ticket_body"]

A prompt declares `path` or `source` plus `key`, never both. The
lockfile records `db:support_triage` as the locator, so moving a prompt
between a file and a table shows up as `MOVED` rather than as a drift.

## the query, not a table name

Every schema I have met puts the prompt somewhere slightly different: a
versions table where the live row is `active = 1`, a JSON column, a join
through a tenant table. A query the operator writes handles all of those
and keeps schema knowledge out of the tool. It takes one named
parameter, `:key`, and must identify exactly one row -- two matching
rows is an error, not a coin flip, because picking one would hide a data
problem behind a pin that looks fine.

The connection is opened read-only. A gate that can write to the thing
it is auditing is a worse gate.

## keys(), and why it is optional

A source that can enumerate its keys lets `verify` report the other half
of the drift problem: a prompt that is live in production and that
nobody declared. A source that cannot enumerate loses that check
entirely, and that is a real reduction in coverage rather than a
cosmetic one -- worth knowing about before choosing a source.

## writing one

Subclass `promptlock.sources.base.Source`, implement `get`, optionally
implement `keys`, and register it:

    [project.entry-points."promptlock.sources"]
    vault = "mypkg.promptlock_source:VaultSource"

A plugin may not shadow a builtin name. A pin whose meaning depends on
what happens to be installed is not a pin.

Constraints on an implementation, all of them learned the dull way:

- `get` is read-only and side-effect free. It runs inside `verify`, in
  CI, on every push.
- `get` returns `str`, decoded. If the storage is bytes, the source owns
  the decode and owns raising on invalid UTF-8.
- No retries with backoff that make a CI job hang for ten minutes. Fail.
- No caching inside the source. `verify` wants the live value; that is
  the entire point of running it.
