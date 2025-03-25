import json

import pytest

from promptlock import lockfile


PINS = [lockfile.Pin(id="b", path="b.md", hash="sha256:bb"),
        lockfile.Pin(id="a", path="a.md", hash="sha256:aa",
                     owner="me", variables=("x",))]


def test_pins_are_sorted():
    doc = json.loads(lockfile.dumps(PINS))
    assert [p["id"] for p in doc["prompts"]] == ["a", "b"]


def test_empty_metadata_is_omitted_not_null():
    doc = json.loads(lockfile.dumps(PINS))
    assert "owner" not in doc["prompts"][1]


def test_serialisation_is_stable():
    assert lockfile.dumps(PINS) == lockfile.dumps(PINS[::-1])


def test_ends_with_exactly_one_newline():
    text = lockfile.dumps(PINS)
    assert text.endswith("}\n")
    assert not text.endswith("\n\n")


def test_roundtrip(tmp_path):
    p = lockfile.write(tmp_path / "promptlock.lock", PINS)
    back = lockfile.read(p)
    assert [x.id for x in back] == ["a", "b"]
    assert back[0].variables == ("x",)


def test_written_file_has_lf_endings(tmp_path):
    p = lockfile.write(tmp_path / "promptlock.lock", PINS)
    assert b"\r\n" not in p.read_bytes()


def test_unknown_lockfile_version_is_refused():
    with pytest.raises(lockfile.LockError):
        lockfile.loads(json.dumps({"lockfile_version": 99}))


def test_wrong_canon_scheme_is_refused():
    doc = {"lockfile_version": 1, "canon_scheme": 0, "prompts": []}
    with pytest.raises(lockfile.LockError) as e:
        lockfile.loads(json.dumps(doc))
    assert "not comparable" in str(e.value)
