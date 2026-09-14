# The lockfile format

`promptlock.lock` is generated, checked in, and read by four of my
own repositories. It is a documented format with a version field, and
every version that has ever been written stays readable.

```json
{
 "canon_scheme": 2,
 "generated_by": "promptlock 1.4.0",
 "lockfile_version": 2,
 "prompts": [
  {
   "hash": "sha256:9f2c1ab4de01...",
   "id": "support_triage",
   "locator": "prompts/support_triage.md",
   "owner": "platform",
   "raw_sha256": "sha256:b71e05c3...",
   "tuned_against": "gpt-4o-mini",
   "variables": ["customer_name", "ticket_body"]
  }
 ]
}
```

## serialisation

Sorted keys, one-space indent, LF line endings, exactly one trailing
newline, UTF-8. All four are tested, and the test is load-bearing:
the file is signed, so the day I "tidy" the writer to use the platform
line ending, every signature I have ever made breaks and the failure
looks like tampering.

## fields

| field | meaning |
|---|---|
| `lockfile_version` | this document's shape. 2. |
| `canon_scheme` | the canonicalisation rules `hash` was computed under |
| `generated_by` | the tool version that wrote it. Informational; never compared. |
| `id` | the registry key. Stable; the thing reports cite. |
| `locator` | `prompts/x.md` for a file, `<source>:<key>` otherwise |
| `hash` | sha256 over the canonical form. The pin. |
| `raw_sha256` | sha256 over the exact bytes. Optional. |
| `owner`, `tuned_against`, `variables`, `optional` | copied from the registry so the lockfile is readable on its own |

`raw_sha256` is the only field whose absence means nothing: it is
omitted for a prompt behind a source, where there are no canonical
bytes to speak of, and for anything a cached run produced.

## versions

| version | change |
|---|---|
| 1 | `path`, which was a filesystem path |
| 2 | `path` renamed to `locator`; `raw_sha256` and `generated_by` added |

`path` had been carrying a locator in practice since sources existed,
which meant a field called `path` containing `db:support_triage`. v2
renames it.

**A v1 lockfile is read, forever.** `path` is mapped onto `locator`
and nothing is lost. `promptlock lock` writes version 2 and prints one
note on stderr saying it upgraded and that no hash changed -- because
the diff renames a field on every line, and a reviewer needs to know
which of the two kinds of churn they are looking at.

A version this build does not know is an error, not a best effort. A
lockfile written by a newer promptlock may use a field this one would
ignore, and silently ignoring a field in a security control is how a
control stops being one.

## what a reader has to do

If you are parsing this file yourself:

1. Check `lockfile_version`. Refuse what you do not know.
2. Check `canon_scheme` against the rules you implement. If you are not
   implementing canonicalisation, do not compute hashes -- compare the
   ones in the file.
3. Read `locator`, falling back to `path`.

And the thing people get wrong: do not compare twelve-character short
hashes. They exist for humans to read aloud.
