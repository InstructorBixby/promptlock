# Changelog

Keep a Changelog format, semver versions.

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
