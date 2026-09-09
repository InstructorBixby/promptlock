import json

from promptlock.commands.main import main


def downgrade_to_v1(project):
    p = project / "promptlock.lock"
    doc = json.loads(p.read_text())
    doc["lockfile_version"] = 1
    for row in doc["prompts"]:
        row["path"] = row.pop("locator")
        row.pop("raw_sha256", None)
    doc.pop("generated_by", None)
    p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def test_verify_accepts_a_v1_lockfile(project, capsys):
    main(["lock"])
    downgrade_to_v1(project)
    assert main(["verify"]) == 0


def test_verify_still_detects_drift_in_a_v1_lockfile(project, capsys):
    main(["lock"])
    downgrade_to_v1(project)
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["verify"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out


def test_lock_upgrades_and_says_so(project, capsys):
    main(["lock"])
    downgrade_to_v1(project)
    assert main(["lock"]) == 0
    err = capsys.readouterr().err
    assert "version 1 to 2" in err
    assert "No hash changed" in err
    doc = json.loads((project / "promptlock.lock").read_text())
    assert doc["lockfile_version"] == 2


def test_the_upgrade_changes_no_hash(project):
    main(["lock"])
    before = {r["id"]: r["hash"] for r in json.loads(
        (project / "promptlock.lock").read_text())["prompts"]}
    downgrade_to_v1(project)
    main(["lock"])
    after = {r["id"]: r["hash"] for r in json.loads(
        (project / "promptlock.lock").read_text())["prompts"]}
    assert before == after


def test_the_note_goes_to_stderr_not_stdout(project, capsys):
    main(["lock"])
    downgrade_to_v1(project)
    main(["lock"])
    out = capsys.readouterr()
    assert "version 1 to 2" in out.err
    assert "version 1 to 2" not in out.out
