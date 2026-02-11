# Signing the lockfile

    promptlock sign --key cosign.key
    promptlock verify --signature-key cosign.pub

Optional. Nothing else needs cosign installed.

## the gap it closes

The lockfile detects tampering with prompt *text*: change the text and
the hash stops matching. It does not detect tampering with *itself*.
Anyone who can edit the lockfile can re-pin a modified prompt, and
`verify` will agree with them, because `verify`'s only question is
whether the text matches the pin.

Here the review is me reading my own diff, which is a weaker control
than it sounds and the honest reason a signature is worth anything at
all. The places it earns its keep are where the lockfile travels
without the repository: a copy attached to a report, one baked into a
container image, one sitting in an engagement folder I will come back
to in a year and want to know I have not edited since.

## what it does not prove

- **Not that the prompt is safe.** It is a hash with a signature on it.
- **Not that the text was reviewed.** It proves whoever held the key
  signed this file at some point.
- **Not that the key holder is trustworthy.** That is the whole
  question and no tool answers it. A signature verified against a key
  that lives in the same repository as the lockfile proves that the
  attacker who could edit one could sign the other.
- **Not freshness.** A valid signature over an old lockfile is still
  valid. If an attacker can serve you a previous lockfile they can roll
  you back to a previous prompt, signature and all. Pin the version you
  expect somewhere outside the signed artefact.

## the serialisation matters

The signature is over the lockfile bytes, so the serialisation has to
be deterministic or a signature valid on Linux is invalid on Windows.
The lockfile is written with sorted keys, one-space indent, explicit LF
and exactly one trailing newline, and there is a test asserting all
four. That test is load-bearing: the day I "tidy" the writer to use
the platform line ending, every signature I have ever made breaks and
the failure looks like tampering.
