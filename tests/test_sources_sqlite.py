import sqlite3

import pytest

from promptlock.sources.base import MissingPrompt, SourceError
from promptlock.sources.sqlite import SqliteSource

Q = "select body from prompts where name = :key and active = 1"


def db(tmp_path, rows):
    p = tmp_path / "prompts.db"
    con = sqlite3.connect(p)
    con.execute("create table prompts (name text, body text, "
                "active int)")
    con.executemany("insert into prompts values (?, ?, ?)", rows)
    con.commit()
    con.close()
    return p


def test_reads_a_row(tmp_path):
    p = db(tmp_path, [("triage", "Classify.\n", 1)])
    assert SqliteSource(p, Q).get("triage") == "Classify.\n"


def test_inactive_rows_are_invisible(tmp_path):
    p = db(tmp_path, [("triage", "old\n", 0)])
    with pytest.raises(MissingPrompt):
        SqliteSource(p, Q).get("triage")


def test_two_live_rows_is_an_error_not_a_coin_flip(tmp_path):
    p = db(tmp_path, [("triage", "a\n", 1), ("triage", "b\n", 1)])
    with pytest.raises(SourceError) as e:
        SqliteSource(p, Q).get("triage")
    assert "exactly one" in str(e.value)


def test_a_query_without_the_parameter_is_refused(tmp_path):
    p = db(tmp_path, [])
    with pytest.raises(SourceError):
        SqliteSource(p, "select body from prompts")


def test_a_non_text_column_is_refused(tmp_path):
    p = db(tmp_path, [("triage", None, 1)])
    with pytest.raises(SourceError) as e:
        SqliteSource(p, Q).get("triage")
    assert "not text" in str(e.value)


def test_missing_database(tmp_path):
    with pytest.raises(SourceError):
        SqliteSource(tmp_path / "nope.db", Q).get("x")


def test_the_connection_is_read_only(tmp_path):
    p = db(tmp_path, [("triage", "a\n", 1)])
    src = SqliteSource(p, Q)
    with pytest.raises(sqlite3.OperationalError):
        with src._connect() as con:
            con.execute("delete from prompts")


def test_keys_when_the_query_is_given(tmp_path):
    p = db(tmp_path, [("a", "x", 1), ("b", "y", 1)])
    src = SqliteSource(p, Q,
                       keys_query="select name from prompts "
                                  "where active = 1")
    assert src.keys() == ["a", "b"]


def test_keys_is_empty_without_one(tmp_path):
    p = db(tmp_path, [("a", "x", 1)])
    assert SqliteSource(p, Q).keys() == []
