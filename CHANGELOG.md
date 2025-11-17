# Changelog

Keep a Changelog format, semver versions.

## [0.5.1]

### Fixed
- `promptlock fmt` wrote the *hashing* canonical form back to the
  file, which includes NFC normalisation. A prompt that
  deliberately contained a decomposed sequence -- a text-handling
  probe, where the sequence was the content -- was silently
  rewritten to the precomposed form. No hash moved, because the
  hash folds exactly that difference, so nothing reported it. The
  probe simply stopped testing what it was written to test.

  `canon.canonical` (hashed, never written) and `canon.formatted`
  (written, never normalises) are now separate. Normalise to
  compare, store raw. `fmt` and `lock` both say so when the two
  disagree. `docs/unicode.md` has the whole thing.

## [0.5.0]

### Changed
- **Canon scheme 2.** CRLF and lone CR fold to LF, and text is NFC
  normalised. Scheme 1 deliberately did neither; a checkout with
  line-ending translation on had every prompt rewritten at
  checkout and `verify` reported drift on all of them. A gate
  whose correctness depends on every checkout being configured
  right is wrong on the machine I am sitting at and right in the
  test suite. **Every hash changes.**
- `verify` refuses to compare across schemes instead of reporting
  drift, and `lock` refuses to overwrite an older-scheme lockfile.

### Added
- `promptlock migrate`, the only command that re-pins across a
  scheme change, printing the old and new hash of every prompt.
  `--dry-run` included.
- `promptlock fmt`, which writes the canonical form back so the
  file in the editor is the text being hashed. Whitespace, line
  endings and the final newline only -- it will not rewrap or
  reword anything.
- `lock` now notes text that is not in NFC rather than folding it
  silently.

## [0.4.0]

### Added
- Eval binding. `.promptlock/evals.jsonl` records
  `(prompt, prompt_hash, suite, metrics, provenance)`, append-only,
  because a result whose prompt has changed is not wrong, it is
  about something else.
- `promptlock eval record|list|check`. `check` reports a result as
  *stale* when the prompt hash it was measured against is not the
  hash pinned now, and exits 1.
- `promptlock eval import` for a promptfuzz run: reads `run.json`
  for seed, corpus hash, mutator and detector sets and versions,
  counts hits from the jsonl beside it.

### Notes
- The importer will not infer a prompt id from an endpoint URL. A
  wrong binding is worse than no binding.

## [0.3.0]

### Added
- `promptlock render --hash` prints three hashes: template,
  variables and rendered output. A variable change moves the
  render hash while the template hash sits still, which is the
  common case nobody notices.
- Content-addressed store under `.promptlock/objects` holding every
  pinned text, so a diff does not depend on git history.
- `promptlock diff`, word level, with whitespace-only changes
  reported as their own outcome rather than mixed in with real
  edits.

### Changed
- Subcommands moved to `promptlock.commands.*`; the console script
  entry point is now `promptlock.commands.main:main`.
- The store keeps the *raw* text under the *canonical* hash, and
  refuses to overwrite an object whose raw bytes differ.

## [0.2.0]

### Added
- `{{name}}` placeholder parsing, with `{{{{name}}}}` as the escape
  for a literal. Single braces are literal text, so a prompt
  containing JSON needs no escaping at all.
- `promptlock render`, which refuses a missing *or* an unknown
  variable rather than substituting an empty string.
- `promptlock check`: declared variables against the placeholders
  actually in the text, contradictory required/optional
  declarations, suspicious placeholder-shaped fragments, and
  prompts with no owner.

### Fixed
- A prompt whose text contained an example template had that
  example read as a required variable, and `render` substituted
  into it. Escaped placeholders fix the parse; `check` now reports
  the shapes it will not substitute instead of leaving them to be
  discovered in a rendered prompt.

## [0.1.0]

### Added
- Canonical serialisation of prompt text (scheme 1) and a
  `sha256:`-prefixed content hash.
- `promptlock.toml` registry: path, owner, model tuned against,
  expected variables.
- `promptlock.lock`: generated, sorted, LF-pinned JSON carrying the
  canon scheme it was written under.
- `promptlock lock`, `promptlock verify`, `promptlock hash`.
- `verify` reports drift, pinned-but-absent and present-but-unpinned
  separately, and exits 1 for any of them.
- A note on stderr for every difference canonicalisation discarded.
