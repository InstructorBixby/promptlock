from promptlock.commands.main import main


def test_render_with_set(project, capsys):
    assert main(["render", "triage", "--set", "ticket=card declined"]) == 0
    assert "card declined" in capsys.readouterr().out


def test_render_with_a_vars_file(project, capsys):
    (project / "vars.json").write_text('{"ticket": "no access"}',
                                       encoding="utf-8")
    assert main(["render", "triage", "--vars", "vars.json"]) == 0
    assert "no access" in capsys.readouterr().out


def test_render_refuses_a_missing_variable(project, capsys):
    assert main(["render", "triage"]) == 2
    assert "no value for ticket" in capsys.readouterr().err


def test_render_refuses_an_unknown_variable(project, capsys):
    assert main(["render", "triage", "--set", "ticket=x",
                 "--set", "tickett=y"]) == 2
    assert "tickett" in capsys.readouterr().err


def test_render_unknown_id_is_exit_2(project):
    assert main(["render", "nope"]) == 2


def test_check_is_clean_on_the_fixture(project):
    assert main(["check"]) == 0


def test_check_catches_a_renamed_placeholder(project, capsys):
    (project / "prompts" / "triage.md").write_text(
        "Classify the ticket.\n\n{{ticket_body}}\n", encoding="utf-8")
    assert main(["check"]) == 1
    out = capsys.readouterr().out
    assert "undeclared" in out
    assert "unused" in out
