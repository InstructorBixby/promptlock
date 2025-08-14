from promptlock.commands.main import main


def test_diff_against_the_pin(project, capsys):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify the ticket quickly.\n\n{{ticket}}\n",
        encoding="utf-8")
    assert main(["diff", "triage"]) == 0
    out = capsys.readouterr().out
    assert "substantive" in out
    assert "[+quickly+]" in out


def test_diff_reports_whitespace_only(project, capsys):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify\nthe ticket.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["diff", "triage"]) == 0
    assert "whitespace only" in capsys.readouterr().out


def test_diff_of_an_unchanged_prompt(project, capsys):
    main(["lock"])
    assert main(["diff", "triage"]) == 0
    assert "identical" in capsys.readouterr().out


def test_diff_against_a_file(project, capsys):
    main(["lock"])
    (project / "other.md").write_text("Something else.\n",
                                      encoding="utf-8")
    assert main(["diff", "triage", "--to", "other.md"]) == 0
    assert "substantive" in capsys.readouterr().out


def test_diff_unknown_id(project):
    main(["lock"])
    assert main(["diff", "nope"]) == 2
