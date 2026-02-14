import json

from promptlock.commands.main import main


def test_json_is_ok_when_clean(project, capsys):
    main(["lock"])
    assert main(["verify", "--format", "json"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["ok"] is True
    assert doc["counts"]["ok"] == 2


def test_json_names_the_drifted_prompt(project, capsys):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["verify", "--format", "json"]) == 1
    doc = json.loads(capsys.readouterr().out)
    assert doc["ok"] is False
    drifted = [i for i in doc["items"] if i["state"] == "drift"]
    assert [i["id"] for i in drifted] == ["triage"]
    assert drifted[0]["pinned_hash"] != drifted[0]["found_hash"]


def test_json_carries_both_paths(project, capsys):
    main(["lock"])
    main(["verify", "--format", "json"])
    doc = json.loads(capsys.readouterr().out)
    item = [i for i in doc["items"] if i["id"] == "triage"][0]
    assert item["pinned_path"] == "prompts/triage.md"


def test_human_output_unchanged(project, capsys):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["verify"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out
