# Releasing

For me, written down because I do it rarely enough to forget.

    # 1. changelog entry, and the version in promptlock/__init__.py
    #    and pyproject.toml. Both. The pipeline refuses the build if
    #    the tag and pyproject disagree.
    # 2.
    git tag -a v1.3.0 -m "v1.3.0"
    git push origin v1.3.0

Everything after that is the `release` job: it reruns ruff, mypy and
the tests, builds the sdist and wheel, prints their sha256 sums into
the log and writes them next to the commit in a `BUILDINFO`, and keeps
the lot as a pipeline artefact that does not expire.

## nothing is published

There is no publish step and no account anywhere. A tag produces a
wheel; the wheel sits on the artefact for that tag; I install it from
there or from a checkout:

    uv pip install -e ".[dev]"      # here
    pipx install ./dist/promptlock-1.3.0-py3-none-any.whl

That is the whole distribution story and it is enough for the number
of machines involved.

## why the tag check exists

I got it wrong once: a tag whose `pyproject.toml` still said the
previous version, a wheel that therefore claimed to be the previous
version, and a `promptlock.lock` in another repository with a
`generated_by` field naming a release that did not contain the code
that wrote it. The check costs four lines and that cost me an evening.

## what the artefact does not prove

That the code is good, or that I did not make a mistake. `BUILDINFO`
gets me from a wheel back to a commit, which is a lookup rather than a
guarantee -- I can edit both ends. There is no third party here to
prove anything to, and pretending otherwise would be the kind of
ceremony this tool exists to argue against.
