# How this fails open

The useful question about a gate is not whether it can crash. It is
whether it can report clean when it should not. This is the list, kept
because I keep having to re-derive it.

## the one that would actually matter

**A canonicalisation collision reachable on purpose.** Two texts a
model treats differently that this tool gives one hash to. The gate
says clean, the deployed instruction is not the reviewed one, and
nothing anywhere complains. Every canon rule is a claim that some
difference does not matter, and a wrong claim here is invisible by
construction. It is the reason scheme 1 declined to fold line endings
rather than guessing.

## the rest, in order of how much they would ruin a week

- **A `verify` that passes when the text differs.** The gate failing
  open is the whole product failing. The `--deployed` path is the
  fragile one: a service that answers with a stale cache looks exactly
  like a service that is in sync.
- **Path traversal out of the object store or the prompt directory**
  from a registry or lockfile I did not write by hand. The lockfile is
  a file an attacker could control if one of these repositories were
  ever compromised, and the object store takes a digest straight from
  it.
- **Anything that executes.** Nothing in here should ever run a
  subprocess except `cosign`, and nothing should ever `eval`
  anything. A path that does is a bug regardless of reachability,
  because the inputs are text files from somewhere else.

## the things that look like holes and are not

- **A hand-edited lockfile.** `verify` believes the lockfile by
  construction; re-pinning a modified prompt satisfies it. Review is
  the control and signing narrows it, and `docs/signing.md` is
  explicit about how little that proves.
- **The content of the prompts.** This tool has no opinion about
  whether a prompt is safe and does not claim to detect injection.
  That is `promptfuzz`, and the two are only useful together.
- **A SQL query in `[source.*]`.** It runs against a read-only
  connection. Beyond that it is my query and my database.
- **A pathological input file.** It is a CLI tool run against my own
  repository. If I point it at a four-gigabyte prompt I get what I
  asked for.
