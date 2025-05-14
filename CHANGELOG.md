# Changelog

Keep a Changelog format, semver versions.

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
