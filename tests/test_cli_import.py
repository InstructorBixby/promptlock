import json
import shutil
from pathlib import Path

from promptlock.commands.main import main

DATA = Path(__file__).parent / "data" / "promptfuzz-run.json"


def stage(project, rows=()):
    out = project / "results"
    out.mkdir()
    shutil.copy(DATA, out / "run.json")
    (out / "run.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return out / "run.json"


def test_import_binds_to_the_pin(project, capsys):
    main(["lock"])
    run = stage(project, [{"hit": True}, {"hit": False}])
    assert main(["eval", "import", "triage", str(run)]) == 0
    out = capsys.readouterr().out
    assert "promptfuzz:injection-core" in out
    assert "rate=0.5" in out


def test_an_edit_after_import_is_stale(project, capsys):
    main(["lock"])
    run = stage(project, [{"hit": False}])
    main(["eval", "import", "triage", str(run)])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    main(["lock"])
    assert main(["eval", "check"]) == 1
    assert "stale    triage" in capsys.readouterr().out


def test_import_carries_the_corpus_hash(project, capsys):
    main(["lock"])
    run = stage(project, [{"hit": False}])
    main(["eval", "import", "triage", str(run)])
    main(["eval", "list", "--json"])
    doc = json.loads(capsys.readouterr().out)
    assert doc[0]["provenance"]["corpus_hash"] == "7c1e4f0a9b2d3e55"


def test_import_needs_a_pinned_prompt(project):
    main(["lock"])
    run = stage(project)
    assert main(["eval", "import", "nope", str(run)]) == 2


def test_import_of_a_missing_run(project, capsys):
    main(["lock"])
    assert main(["eval", "import", "triage", "nope.json"]) == 2
    assert "no run.json" in capsys.readouterr().err
