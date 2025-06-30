import json

from promptlock.cli import main


def test_render_hash_prints_three_hashes(project, capsys):
    assert main(["render", "triage", "--set", "ticket=x", "--hash"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert set(doc) == {"template", "variables", "render"}


def test_template_hash_matches_the_lockfile(project, capsys):
    main(["lock"])
    pinned = json.loads((project / "promptlock.lock").read_text())
    by_id = {p["id"]: p for p in pinned["prompts"]}
    main(["render", "triage", "--set", "ticket=x", "--hash"])
    doc = json.loads(capsys.readouterr().out)
    assert doc["template"] == by_id["triage"]["hash"]


def test_render_hash_moves_with_the_variable(project, capsys):
    main(["render", "triage", "--set", "ticket=a", "--hash"])
    a = json.loads(capsys.readouterr().out)
    main(["render", "triage", "--set", "ticket=b", "--hash"])
    b = json.loads(capsys.readouterr().out)
    assert a["template"] == b["template"]
    assert a["render"] != b["render"]
