import json

from promptlock.commands.main import main


def test_markdown_lists_every_prompt(project, capsys):
    main(["lock"])
    assert main(["export"]) == 0
    out = capsys.readouterr().out
    assert "| `triage` |" in out
    assert "| `digest` |" in out
    assert "No eval results are bound" in out


def test_markdown_includes_a_result(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "injection-core",
          "--tool", "promptfuzz",
          "--metrics", '{"sends": 100, "hits": 1, "rate": 0.01}'])
    main(["export"])
    out = capsys.readouterr().out
    assert "injection-core" in out
    assert "rate=0.01" in out
    assert "no longer pinned" not in out


def test_markdown_flags_a_stale_result(project, capsys):
    main(["lock"])
    main(["eval", "record", "triage", "--suite", "s"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    main(["lock"])
    main(["export"])
    assert "no longer pinned" in capsys.readouterr().out


def test_json_carries_the_full_hash(project, capsys):
    main(["lock"])
    assert main(["export", "--format", "json"]) == 0
    rows = {r["id"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["triage"]["hash"].startswith("sha256:")
    assert rows["triage"]["variables"] == ["ticket"]


def test_export_names_the_canon_scheme(project, capsys):
    main(["lock"])
    main(["export"])
    assert "scheme 2" in capsys.readouterr().out
