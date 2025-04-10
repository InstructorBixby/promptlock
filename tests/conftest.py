import pytest


REGISTRY = """\
[prompt.triage]
path = "prompts/triage.md"
owner = "platform"
variables = ["ticket"]

[prompt.digest]
path = "prompts/digest.md"
owner = "platform"
variables = ["thread"]
"""

TRIAGE = "Classify the ticket.\n\n{{ticket}}\n"
DIGEST = "Summarise the thread.\n\n{{thread}}\n"


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A minimal checked-out project, cwd set to its root."""
    (tmp_path / "prompts").mkdir()
    (tmp_path / "promptlock.toml").write_text(REGISTRY, encoding="utf-8")
    (tmp_path / "prompts" / "triage.md").write_text(TRIAGE,
                                                    encoding="utf-8")
    (tmp_path / "prompts" / "digest.md").write_text(DIGEST,
                                                    encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path
