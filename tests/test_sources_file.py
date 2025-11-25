import pytest

from promptlock import sources
from promptlock.sources.base import MissingPrompt


def test_reads_a_file(tmp_path):
    (tmp_path / "a.md").write_text("hi\n", encoding="utf-8")
    src = sources.FileSource(tmp_path)
    assert src.get("a.md") == "hi\n"


def test_missing_file(tmp_path):
    with pytest.raises(MissingPrompt):
        sources.FileSource(tmp_path).get("nope.md")


def test_keys_finds_prompt_extensions(tmp_path):
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")
    (tmp_path / "c.png").write_bytes(b"x")
    assert sources.FileSource(tmp_path).keys() == ["a.md", "b.txt"]


def test_build_by_kind(tmp_path):
    src = sources.build("file", {"root": str(tmp_path)})
    assert src.kind == "file"


def test_unknown_kind(tmp_path):
    with pytest.raises(sources.SourceError):
        sources.build("carrier-pigeon", {})
