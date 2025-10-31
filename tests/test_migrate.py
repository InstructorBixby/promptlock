import json

from promptlock.commands.main import main


def downgrade(project):
    """Rewrite the lockfile as if an older scheme had produced it."""
    p = project / "promptlock.lock"
    doc = json.loads(p.read_text())
    doc["canon_scheme"] = 1
    for row in doc["prompts"]:
        row["hash"] = "sha256:" + "0" * 64
    p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def test_verify_refuses_an_older_scheme(project, capsys):
    main(["lock"])
    downgrade(project)
    assert main(["verify"]) == 2
    assert "not comparable" in capsys.readouterr().err


def test_lock_refuses_to_quietly_rewrite(project, capsys):
    main(["lock"])
    downgrade(project)
    assert main(["lock"]) == 2
    assert "promptlock migrate" in capsys.readouterr().err


def test_migrate_rewrites_and_reports_every_hash(project, capsys):
    main(["lock"])
    downgrade(project)
    assert main(["migrate"]) == 0
    out = capsys.readouterr().out
    assert "canon scheme 1 -> 2" in out
    assert "2 hash(es) changed" in out
    assert main(["verify"]) == 0


def test_migrate_dry_run_writes_nothing(project, capsys):
    main(["lock"])
    downgrade(project)
    before = (project / "promptlock.lock").read_text()
    assert main(["migrate", "--dry-run"]) == 0
    assert (project / "promptlock.lock").read_text() == before


def test_migrate_on_a_current_lockfile_is_a_noop(project, capsys):
    main(["lock"])
    assert main(["migrate"]) == 0
    assert "already scheme 2" in capsys.readouterr().out


def test_migrate_without_a_lockfile(project, capsys):
    assert main(["migrate"]) == 2
