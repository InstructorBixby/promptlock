import sqlite3
import textwrap

import pytest

from promptlock import registry
from promptlock.commands.main import main


def make_db(root):
    con = sqlite3.connect(root / "prompts.db")
    con.execute("create table prompts (name text, body text, active int)")
    con.executemany("insert into prompts values (?, ?, ?)", [
        ("triage", "Classify the ticket.\n\n{{ticket}}\n", 1),
        ("stray", "Nobody declared me.\n", 1),
    ])
    con.commit()
    con.close()


TOML = textwrap.dedent("""\
    [source.db]
    kind = "sqlite"
    path = "prompts.db"
    query = "select body from prompts where name = :key and active = 1"
    keys_query = "select name from prompts where active = 1"

    [prompt.triage]
    source = "db"
    key = "triage"
    owner = "platform"
    variables = ["ticket"]
    """)


@pytest.fixture
def dbproject(tmp_path, monkeypatch):
    make_db(tmp_path)
    (tmp_path / "promptlock.toml").write_text(TOML, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_locks_a_prompt_from_a_database(dbproject, capsys):
    assert main(["lock"]) == 0
    assert "locked 1 prompt" in capsys.readouterr().out


def test_the_lockfile_records_the_locator(dbproject):
    main(["lock"])
    text = (dbproject / "promptlock.lock").read_text()
    assert '"db:triage"' in text


def test_an_admin_page_edit_is_drift(dbproject, capsys):
    main(["lock"])
    con = sqlite3.connect(dbproject / "prompts.db")
    con.execute("update prompts set body = ? where name = 'triage'",
                ("Classify it fast.\n\n{{ticket}}\n",))
    con.commit()
    con.close()
    assert main(["verify", "--no-undeclared"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out


def test_an_undeclared_live_prompt_is_reported(dbproject, capsys):
    main(["lock"])
    assert main(["verify"]) == 1
    assert "UNKNOWN  db:stray" in capsys.readouterr().out


def test_path_and_source_together_is_an_error(dbproject):
    (dbproject / "promptlock.toml").write_text(
        TOML + 'path = "x.md"\n', encoding="utf-8")
    with pytest.raises(registry.RegistryError):
        registry.load(dbproject / "promptlock.toml")


def test_a_source_reference_with_no_declaration(tmp_path):
    (tmp_path / "promptlock.toml").write_text(
        '[prompt.a]\nsource = "nope"\nkey = "a"\n', encoding="utf-8")
    with pytest.raises(registry.RegistryError) as e:
        registry.load(tmp_path / "promptlock.toml")
    assert "no [source.nope]" in str(e.value)


def test_a_source_without_a_key(tmp_path):
    (tmp_path / "promptlock.toml").write_text(
        TOML.replace('key = "triage"', ""), encoding="utf-8")
    with pytest.raises(registry.RegistryError):
        registry.load(tmp_path / "promptlock.toml")
