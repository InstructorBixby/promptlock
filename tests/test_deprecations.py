import json

from promptlock import deprecations
from promptlock.commands.main import main


def test_old_flag_still_works(project, capsys):
    main(["lock"])
    assert main(["verify", "--no-undeclared"]) == 0
    assert "--no-undeclared is deprecated" in capsys.readouterr().err


def test_new_flag_warns_about_nothing(project, capsys):
    main(["lock"])
    assert main(["verify", "--skip-undeclared"]) == 0
    assert "deprecated" not in capsys.readouterr().err


def test_the_old_flag_does_not_change_the_exit_code(project):
    main(["lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["verify", "--no-undeclared"]) == 1


def test_the_warning_is_not_on_stdout(project, capsys):
    main(["lock"])
    main(["verify", "--no-undeclared", "--format", "json"])
    out = capsys.readouterr()
    assert "deprecated" in out.err
    # The whole point: stdout has to stay parseable.
    json.loads(out.out)


def test_json_emits_both_field_names(project, capsys):
    main(["lock"])
    main(["verify", "--format", "json"])
    item = json.loads(capsys.readouterr().out)["items"][0]
    assert item["pinned_locator"] == item["pinned_path"]


def test_with_aliases_does_not_invent_a_field():
    assert deprecations.with_aliases({"state": "ok"}) == {"state": "ok"}
