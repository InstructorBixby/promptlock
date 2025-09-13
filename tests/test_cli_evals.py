from promptlock.commands.main import main


def test_record_then_check_is_current(project, capsys):
    main(["lock"])
    assert main(["eval", "record", "triage", "--suite", "injection-core",
                 "--tool", "promptfuzz",
                 "--metrics", '{"sends": 100, "hits": 1}']) == 0
    assert main(["eval", "check"]) == 0


def test_an_edit_makes_the_result_stale(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "injection-core"])
    (project / "prompts" / "triage.md").write_text(
        "Classify, and be careful.\n\n{{ticket}}\n", encoding="utf-8")
    main(["lock"])
    assert main(["eval", "check"]) == 1
    assert "stale" in capsys.readouterr().out


def test_record_needs_a_lockfile(project, capsys):
    assert main(["eval", "record", "triage", "--suite", "s"]) == 2


def test_record_needs_a_pinned_id(project, capsys):
    main(["lock"])
    assert main(["eval", "record", "nope", "--suite", "s"]) == 2
    assert "not in the lockfile" in capsys.readouterr().err


def test_list_prints_the_hash(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "s"])
    main(["eval", "list"])
    out = capsys.readouterr().out
    assert "triage" in out


def test_require_results_fails_for_an_unmeasured_prompt(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "s"])
    assert main(["eval", "check", "--require-results"]) == 1
    assert "missing  digest" in capsys.readouterr().out
