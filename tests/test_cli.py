from promptlock.cli import main


def test_lock_then_verify_is_clean(project, capsys):
    assert main(["lock"]) == 0
    assert main(["verify"]) == 0
    assert "2 prompt(s) match" in capsys.readouterr().out


def test_verify_detects_an_edit(project, capsys):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify the ticket, and be brief.\n\n{{ticket}}\n",
        encoding="utf-8")
    assert main(["verify"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out


def test_verify_ignores_a_trailing_space(project):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify the ticket.   \n\n{{ticket}}\n", encoding="utf-8")
    assert main(["verify"]) == 0


def test_verify_reports_a_new_unpinned_prompt(project, capsys):
    main(["lock"])
    with (project / "promptlock.toml").open("a", encoding="utf-8") as fh:
        fh.write('\n[prompt.extra]\npath = "prompts/digest.md"\n')
    assert main(["verify"]) == 1
    assert "UNPINNED extra" in capsys.readouterr().out


def test_verify_reports_a_removed_prompt(project, capsys):
    main(["lock"])
    (project / "promptlock.toml").write_text(
        '[prompt.triage]\npath = "prompts/triage.md"\n',
        encoding="utf-8")
    assert main(["verify"]) == 1
    assert "MISSING  digest" in capsys.readouterr().out


def test_missing_lockfile_is_exit_2(project, capsys):
    assert main(["verify"]) == 2
    assert "no lockfile" in capsys.readouterr().err


def test_hash_does_not_need_a_registry(project, capsys):
    assert main(["hash", "prompts/triage.md"]) == 0
    assert capsys.readouterr().out.startswith("sha256:")
