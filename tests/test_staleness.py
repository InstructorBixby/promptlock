from promptlock import staleness
from promptlock.evals import Record
from promptlock.lockfile import Pin


PIN = {"a": Pin(id="a", path="a.md", hash="sha256:aa")}


def rec(h, suite="s"):
    return Record(prompt="a", prompt_hash=h, suite=suite)


def test_matching_hash_is_current():
    st = staleness.assess(PIN, {("a", "s"): rec("sha256:aa")})
    assert [s.state for s in st] == [staleness.CURRENT]


def test_moved_hash_is_stale():
    st = staleness.assess(PIN, {("a", "s"): rec("sha256:bb")})
    assert st[0].state == staleness.STALE
    assert "pinned is" in str(st[0])


def test_no_result_is_missing():
    st = staleness.assess(PIN, {}, suites=["s"])
    assert st[0].state == staleness.MISSING


def test_no_suites_at_all_reports_nothing_to_say():
    assert staleness.assess(PIN, {}) == []


def test_several_suites():
    records = {("a", "s"): rec("sha256:aa"),
               ("a", "t"): rec("sha256:bb", suite="t")}
    st = staleness.assess(PIN, records)
    assert sorted(s.state for s in st) == ["current", "stale"]
