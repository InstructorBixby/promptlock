# When the registry gets big

Forty prompts is instant. Eleven hundred, in a monorepo, with the gate
on a pre-commit hook, is eight seconds -- which is long enough that
people start passing `--no-verify`, and a gate people skip is not a
gate.

    promptlock --cache lock
    promptlock --cache status

The cache is keyed on `(path, size, mtime_ns)`, not on content, because
the entire point is to avoid reading the content. That makes it a
heuristic, with one known miss: a file rewritten within a single mtime
tick, at exactly the same size, with different content, reads as
unchanged. Every build system takes the same bet.

## where the cache is not used

- `promptlock verify`. This is the gate. It reads every byte, every
  time, and no flag turns that off. A gate with a cache in it answers a
  question about the cache.
- anything involving a signature.
- any prompt behind a source. A database row has no mtime, and a cached
  answer for "what is live right now" is not an answer.

## if eight seconds is still too slow

Most of the remaining cost is process startup and reading a thousand
small files. Two things that help more than anything in here: put the
prompt directory on something that is not a network filesystem, and
scope the pre-commit hook to `^prompts/` so it does not run on commits
that cannot possibly have changed a prompt.
