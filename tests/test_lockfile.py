import json

import pytest

from promptlock import canon, lockfile


PINS = [lockfile.Pin(id="b", locator="b.md", hash="sha256:bb"),
        lockfile.Pin(id="a", locator="a.md", hash="sha256:aa",
                     owner="me", variables=("x",))]


def test_pins_are_sorted():
    doc = json.loads(lockfile.dumps(PINS))
    assert [p["id"] for p in doc["prompts"]] == ["a", "b"]


def test_writes_the_current_version():
    doc = json.loads(lockfile.dumps(PINS))
    assert doc["lockfile_version"] == 2


def test_writes_locator_not_path():
    doc = json.loads(lockfile.dumps(PINS))
    assert doc["prompts"][0]["locator"] == "a.md"
    assert "path" not in doc["prompts"][0]


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


def test_generated_by_is_optional():
    assert "generated_by" not in json.loads(lockfile.dumps(PINS))
    doc = json.loads(lockfile.dumps(PINS, generated_by="promptlock 1.4.0"))
    assert doc["generated_by"] == "promptlock 1.4.0"


# --- v1 compatibility, which is permanent --------------------------

V1 = {
    "lockfile_version": 1,
    "canon_scheme": canon.SCHEME,
    "prompts": [{"id": "a", "path": "prompts/a.md",
                 "hash": "sha256:aa", "owner": "me"},
                {"id": "b", "path": "db:b", "hash": "sha256:bb"}],
}


def test_a_v1_lockfile_still_reads():
    pins = lockfile.loads(json.dumps(V1))
    assert [p.id for p in pins] == ["a", "b"]


def test_v1_path_becomes_locator():
    pins = lockfile.loads(json.dumps(V1))
    assert pins[0].locator == "prompts/a.md"
    assert pins[1].locator == "db:b"


def test_v1_has_no_raw_sha256_and_that_is_fine():
    assert lockfile.loads(json.dumps(V1))[0].raw_sha256 == ""


def test_pin_path_is_still_readable_as_an_alias():
    assert lockfile.loads(json.dumps(V1))[0].path == "prompts/a.md"


def test_version_of():
    assert lockfile.version_of(json.dumps(V1)) == 1
    assert lockfile.version_of(lockfile.dumps(PINS)) == 2
    assert lockfile.version_of("{not json") is None


def test_an_unknown_future_version_is_refused():
    with pytest.raises(lockfile.LockError) as e:
        lockfile.loads(json.dumps({"lockfile_version": 99}))
    assert "readable: 1, 2" in str(e.value)


def test_wrong_canon_scheme_is_refused():
    doc = {"lockfile_version": 2, "canon_scheme": 0, "prompts": []}
    with pytest.raises(lockfile.LockError) as e:
        lockfile.loads(json.dumps(doc))
    assert "not comparable" in str(e.value)


def test_raw_digest_separates_canonically_equal_texts():
    a, b = "hi\n", "hi   \n"
    assert canon.digest(a) == canon.digest(b)
    assert lockfile.raw_digest(a) != lockfile.raw_digest(b)
