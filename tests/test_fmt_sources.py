import sqlite3
import textwrap

import pytest

from promptlock.commands.main import main

TOML = textwrap.dedent("""\
    [source.db]
    kind = "sqlite"
    path = "prompts.db"
    query = "select body from prompts where name = :key"

    [prompt.triage]
    source = "db"
    key = "triage"
    owner = "platform"
    variables = ["ticket"]
    """)


@pytest.fixture
def dbproject(tmp_path, monkeypatch):
    con = sqlite3.connect(tmp_path / "prompts.db")
    con.execute("create table prompts (name text, body text)")
    con.execute("insert into prompts values ('triage', ?)",
                ("Classify.   \n\n{{ticket}}\n",))
    con.commit()
    con.close()
    (tmp_path / "promptlock.toml").write_text(TOML, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_fmt_skips_a_source_backed_prompt(dbproject, capsys):
    assert main(["fmt"]) == 0
    out = capsys.readouterr().out
    assert "skipped, not a file" in out
    assert "reformatted 0 file(s)" in out


def test_fmt_does_not_create_a_stray_file(dbproject):
    main(["fmt"])
    names = sorted(p.name for p in dbproject.iterdir())
    assert names == ["promptlock.toml", "prompts.db"]


def test_fmt_check_is_clean_with_only_sources(dbproject):
    assert main(["fmt", "--check"]) == 0
