import pytest

from promptlock import canon, store


def test_roundtrip(tmp_path):
    s = store.Store(tmp_path)
    d = s.put("hello\n")
    assert s.get(d) == "hello\n"


def test_digest_matches_canon(tmp_path):
    s = store.Store(tmp_path)
    assert s.put("hello\n") == canon.digest("hello\n")


def test_raw_bytes_are_preserved_not_canonicalised(tmp_path):
    s = store.Store(tmp_path)
    d = s.put("hello   \n")
    assert s.get(d) == "hello   \n"


def test_putting_the_same_text_twice_is_fine(tmp_path):
    s = store.Store(tmp_path)
    assert s.put("hi\n") == s.put("hi\n")


def test_canonically_equal_but_different_raw_is_refused(tmp_path):
    s = store.Store(tmp_path)
    s.put("hi\n")
    with pytest.raises(store.StoreError) as e:
        s.put("hi  \n")
    assert "different raw bytes" in str(e.value)


def test_force_put_replaces(tmp_path):
    s = store.Store(tmp_path)
    d = s.put("hi\n")
    s.force_put("hi  \n")
    assert s.get(d) == "hi  \n"


def test_missing_object(tmp_path):
    s = store.Store(tmp_path)
    with pytest.raises(store.StoreError):
        s.get("sha256:" + "0" * 64)


def test_a_non_digest_is_rejected(tmp_path):
    s = store.Store(tmp_path)
    with pytest.raises(store.StoreError):
        s.has("deadbeef")


def test_a_digest_shaped_path_traversal_is_rejected(tmp_path):
    s = store.Store(tmp_path)
    with pytest.raises(store.StoreError):
        s.get("sha256:" + "../" * 21 + "etcpasswd")


def test_has(tmp_path):
    s = store.Store(tmp_path)
    d = s.put("hi\n")
    assert s.has(d)
    assert not s.has("sha256:" + "1" * 64)
