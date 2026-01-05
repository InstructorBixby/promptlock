# Installing

From the checkout, which is how it runs on this machine:

    uv pip install -e ".[dev]"

From the wheel a tag built, which is how it runs anywhere else:

    pipx install ./dist/promptlock-0.6.0-py3-none-any.whl

Python 3.11 or later. **No runtime dependencies.** That is a design
constraint rather than a happy accident: this thing runs in front of
every gate I have, and every dependency it took on would be one all
of those inherit for the privilege of hashing a text file.

Optional, and needed only by the command that uses it:

| | |
|---|---|
| `cosign` on PATH | `promptlock sign`, `verify --signature-key` |

## in a pipeline

Install the pinned wheel, not a floating anything. The whole
proposition is that a hash means the same thing tomorrow, and a
tooling update that moves a canon scheme would turn every prompt in
the repository into a drift report. A canon scheme bump is a minor
release, so `~=1.0` would not be enough on its own even if there were
somewhere to install from.

## which build this is

`promptlock --version`, and the `BUILDINFO` next to the wheel in the
pipeline artefact for that tag. Between those and the tag here I can
get from a lockfile's `generated_by` back to the code that wrote it,
which is the only question I have ever actually needed to answer
about a build.
