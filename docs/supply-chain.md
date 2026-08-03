# What this depends on

A tool whose whole claim is that a hash means the same thing next
quarter should be able to say what went into it. Here is all of it.

| | |
|---|---|
| runtime dependencies | none, and a pipeline job fails if that stops being true |
| build dependencies | `setuptools` and `build`, in the release job only |
| dev dependencies | pinned in `constraints-dev.txt` |
| where a wheel is built | the runner on this box, from a tag |
| how it gets anywhere else | I copy it |

## why no runtime dependencies is a property and not a brag

This runs in front of every gate I have: the pre-commit hook in each
repository that keeps a lockfile, the pipeline job on each of them,
and the thing `plays` shells out to. Every dependency it took on would be one all of those
inherit for the privilege of hashing a text file, and each one is a
package that can change under me between a Tuesday and a Wednesday.
The standard library has `hashlib`, `tomllib`, `json`, `sqlite3`,
`difflib`, `unicodedata` and `urllib`, which is the entire shopping
list.

The two things that are not in the standard library are deliberately
not dependencies either:

- **cosign**, used by `promptlock sign`, is shelled out to and must
  already be on PATH. The only command that needs it is the one that
  never runs in a gate.
- **mkdocs-material**, for the docs, is in a `docs` extra and is
  never installed by a normal install.

## the thing I would attack

Me. The gate believes the lockfile, the lockfile is written by this
tool, and this tool runs on my machine with my hands on it. Signing a
lockfile narrows that to "the bytes have not changed since I signed
them", which is a real and small claim. It does not make me a
trustworthy source about my own prompts, and nothing here could.
