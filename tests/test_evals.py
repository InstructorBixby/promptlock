import pytest

from promptlock import evals


def rec(**kw):
    base = dict(prompt="a", prompt_hash="sha256:aa", suite="s",
                tool="promptfuzz", metrics={"hits": 1})
    base.update(kw)
    return evals.Record(**base)


def test_recorded_is_filled_in():
    assert rec().recorded


def test_an_explicit_timestamp_is_kept():
    assert rec(recorded="x").recorded == "x"


def test_roundtrip(tmp_path):
    log = evals.EvalLog(tmp_path / "evals.jsonl")
    log.append(rec())
    assert [r.prompt for r in log.all()] == ["a"]


def test_append_only(tmp_path):
    log = evals.EvalLog(tmp_path / "evals.jsonl")
    log.append(rec(prompt_hash="sha256:aa"))
    log.append(rec(prompt_hash="sha256:bb"))
    assert len(log.all()) == 2


def test_latest_is_per_prompt_and_suite(tmp_path):
    log = evals.EvalLog(tmp_path / "evals.jsonl")
    log.append(rec(prompt_hash="sha256:aa"))
    log.append(rec(prompt_hash="sha256:bb"))
    log.append(rec(suite="other"))
    latest = log.latest()
    assert latest[("a", "s")].prompt_hash == "sha256:bb"
    assert ("a", "other") in latest


def test_missing_file_is_empty_not_an_error(tmp_path):
    assert evals.EvalLog(tmp_path / "nope.jsonl").all() == []


def test_blank_lines_are_skipped(tmp_path):
    p = tmp_path / "evals.jsonl"
    evals.EvalLog(p).append(rec())
    with p.open("a", encoding="utf-8") as fh:
        fh.write("\n")
    assert len(evals.EvalLog(p).all()) == 1


def test_a_bad_line_names_the_line_number(tmp_path):
    p = tmp_path / "evals.jsonl"
    evals.EvalLog(p).append(rec())
    with p.open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    with pytest.raises(evals.EvalError) as e:
        evals.EvalLog(p).all()
    assert ":2:" in str(e.value)


def test_an_unknown_field_is_an_error(tmp_path):
    p = tmp_path / "evals.jsonl"
    p.write_text('{"prompt": "a", "prompt_hash": "x", "suite": "s", '
                 '"future": 1}\n', encoding="utf-8")
    with pytest.raises(evals.EvalError):
        evals.EvalLog(p).all()


def test_written_with_lf(tmp_path):
    p = tmp_path / "evals.jsonl"
    evals.EvalLog(p).append(rec())
    assert b"\r\n" not in p.read_bytes()
