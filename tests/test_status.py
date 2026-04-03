import json

from promptlock.commands.main import main


def test_status_without_a_lockfile_still_works(project, capsys):
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "triage" in out
    assert "no eval result" in out


def test_status_shows_the_pin(project, capsys):
    main(["lock"])
    assert main(["status", "--json"]) == 0
    rows = {r["id"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["triage"]["pinned"] != "-"
    assert rows["triage"]["owner"] == "platform"


def test_status_reports_a_current_result(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "s"])
    main(["status", "--json"])
    rows = {r["id"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["triage"]["results"] == "current"
    assert rows["digest"]["results"] == "none"


def test_status_reports_a_stale_result(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "s"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    main(["lock"])
    main(["status", "--json"])
    rows = {r["id"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["triage"]["results"] == "stale"


def test_status_names_unowned_prompts(project, capsys):
    (project / "promptlock.toml").write_text(
        '[prompt.triage]\npath = "prompts/triage.md"\n'
        'variables = ["ticket"]\n', encoding="utf-8")
    main(["status"])
    assert "no owner: triage" in capsys.readouterr().out
