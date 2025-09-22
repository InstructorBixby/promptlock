import json
import shutil
from pathlib import Path

import pytest

from promptlock.importers import promptfuzz

DATA = Path(__file__).parent / "data" / "promptfuzz-run.json"


def run_dir(tmp_path, rows=()):
    shutil.copy(DATA, tmp_path / "run.json")
    if rows:
        (tmp_path / "run.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in rows),
            encoding="utf-8")
    return tmp_path / "run.json"


def test_reads_provenance(tmp_path):
    rec = promptfuzz.read(run_dir(tmp_path), prompt="triage",
                          prompt_hash="sha256:aa")
    assert rec.provenance["seed"] == 11
    assert rec.provenance["corpus_hash"] == "7c1e4f0a9b2d3e55"
    assert rec.tool_version == "1.3.0"


def test_suite_defaults_to_the_corpus(tmp_path):
    rec = promptfuzz.read(run_dir(tmp_path), prompt="triage",
                          prompt_hash="sha256:aa")
    assert rec.suite == "promptfuzz:injection-core"


def test_counts_from_the_jsonl(tmp_path):
    rows = [{"hit": False}, {"hit": True}, {"hit": False},
            {"hit": False}]
    rec = promptfuzz.read(run_dir(tmp_path, rows), prompt="triage",
                          prompt_hash="sha256:aa")
    assert rec.metrics == {"sends": 4, "hits": 1, "rate": 0.25}


def test_no_jsonl_means_no_rate(tmp_path):
    rec = promptfuzz.read(run_dir(tmp_path), prompt="triage",
                          prompt_hash="sha256:aa")
    assert rec.metrics == {}
    assert rec.provenance["planned_sends"] == 4200


def test_the_prompt_is_never_guessed(tmp_path):
    with pytest.raises(TypeError):
        promptfuzz.read(run_dir(tmp_path))


def test_a_foreign_run_json_is_refused(tmp_path):
    (tmp_path / "run.json").write_text('{"tool": "something-else"}',
                                       encoding="utf-8")
    with pytest.raises(promptfuzz.ImportError_):
        promptfuzz.read(tmp_path / "run.json", prompt="a",
                        prompt_hash="sha256:aa")


def test_missing_file(tmp_path):
    with pytest.raises(promptfuzz.ImportError_):
        promptfuzz.read(tmp_path / "nope.json", prompt="a",
                        prompt_hash="sha256:aa")
