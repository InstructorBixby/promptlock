import os

from promptlock.cache import HashCache


def test_roundtrip(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    c = HashCache(tmp_path / "cache.json")
    assert c.get(f) is None
    c.put(f, "sha256:aa")
    assert c.get(f) == "sha256:aa"


def test_survives_a_flush(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    c = HashCache(tmp_path / "cache.json")
    c.put(f, "sha256:aa")
    c.flush()
    assert HashCache(tmp_path / "cache.json").get(f) == "sha256:aa"


def test_an_mtime_change_misses(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    c = HashCache(tmp_path / "cache.json")
    c.put(f, "sha256:aa")
    os.utime(f, ns=(0, 0))
    assert c.get(f) is None


def test_a_size_change_misses(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    c = HashCache(tmp_path / "cache.json")
    c.put(f, "sha256:aa")
    f.write_text("hi there\n")
    assert c.get(f) is None


def test_disabled_never_hits(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    c = HashCache(tmp_path / "cache.json", enabled=False)
    c.put(f, "sha256:aa")
    assert c.get(f) is None
    c.flush()
    assert not (tmp_path / "cache.json").exists()


def test_a_corrupt_cache_is_an_empty_cache(tmp_path):
    (tmp_path / "cache.json").write_text("{not json")
    f = tmp_path / "a.md"
    f.write_text("hi\n")
    assert HashCache(tmp_path / "cache.json").get(f) is None


def test_a_missing_file_is_never_cached(tmp_path):
    c = HashCache(tmp_path / "cache.json")
    c.put(tmp_path / "gone.md", "sha256:aa")
    assert c.get(tmp_path / "gone.md") is None
