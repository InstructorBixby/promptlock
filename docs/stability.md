# Stability promise

From 1.0, these are public and break only in a major version.

## formats

- the lockfile JSON shape, and `lockfile_version`
- the `canon_scheme` number and the canonicalisation rules behind each
- the eval record fields in `.promptlock/evals.jsonl`
- the layout of `.promptlock/objects`

## interfaces

- `promptlock.sources.base.Source`: `get`, `keys`, `describe`, `kind`
- the `promptlock.sources` entry-point group
- `promptlock.canon`: `canonical`, `formatted`, `digest`, `short`,
  `lossy`, `is_nfc`, `SCHEME`

## command line

- exit codes 0, 1, 2
- the subcommand names, and the meaning of each
- the `verify --format json` field names (fields may be *added*)
- the `DRIFT` / `MISSING` / `UNPINNED` / `MOVED` / `UNKNOWN` labels

## explicitly not public

- the human-readable output text, beyond those labels
- `promptlock.report`, `promptlock.project`, `promptlock.diffrender`
- anything under `promptlock.commands`
- the twelve-character short hash as a lookup key. It is for humans.
  Twelve hex characters is 48 bits, which is fine for reading aloud and
  not fine as an identifier, and the day two prompts in one registry
  collide there I want that to be a display bug and not a data bug.

## a canon scheme bump is a minor release

This is the one that looks wrong and is deliberate. A scheme bump
changes every hash, which sounds major. But the *mechanism* for it --
`verify` refusing to compare across schemes, `lock` refusing to
overwrite, `migrate` being the only command that re-pins -- is itself
part of the stability promise, and it has worked twice. Calling each
bump a major release would make the version number a count of Unicode
opinions.

## deprecation policy

Nothing public disappears without a release that still accepts it.

The reason is not an audience. It is that the things calling this are
mine: the pre-commit stanza in `plays`, the gate in two engagement
repositories, the reporting glue that reads `verify --format json`,
and at least one scratch script I have forgotten about. A flag I
rename here fails in a repository I am not looking at, usually on the
morning I needed that repository to work. The shim costs four lines.
The alternative has already cost me an afternoon.

| | |
|---|---|
| notice period | at least two minor releases, and at least one in which the replacement exists |
| a renamed CLI flag | the old spelling keeps working and prints one line to stderr naming the new one |
| a renamed JSON field | both fields are emitted for the whole notice period; the old one is removed in a major release |
| a renamed lockfile field | the reader accepts both; the writer emits the new one and bumps `lockfile_version` |
| a removed subcommand | kept as a stub that explains what to run instead, for the notice period |
| a changed exit code | major only, no exceptions |

Deprecation warnings go to **stderr and never to stdout**. Something
parses stdout, and a warning in the middle of a JSON document is a
breaking change dressed as a courtesy. For the same reason a
deprecation never changes an exit code: a gate that starts failing
because of a rename is a gate people switch off.

Every deprecation gets a changelog entry under `### Deprecated` in the
release that introduces it, and a second entry under `### Removed` in
the release that finishes the job. Both say the version the removal
happens in.
