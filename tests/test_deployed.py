import json

import pytest

from promptlock import canon, deployed
from promptlock.commands.main import main


def test_parse_accepts_a_good_document():
    doc = {"canon_scheme": 2, "prompts": {"a": "sha256:" + "0" * 64}}
    out = deployed.parse(doc)
    assert out["prompts"]["a"].startswith("sha256:")


def test_parse_rejects_a_missing_prompts_object():
    with pytest.raises(deployed.DeployedError):
        deployed.parse({"canon_scheme": 2})


def test_parse_rejects_a_bare_hex_hash():
    with pytest.raises(deployed.DeployedError) as e:
        deployed.parse({"prompts": {"a": "0" * 64}})
    assert "not a sha256: digest" in str(e.value)


def test_parse_rejects_a_non_object_prompts():
    with pytest.raises(deployed.DeployedError):
        deployed.parse({"prompts": ["a"]})


def _serve(monkeypatch, doc):
    def fake_fetch(url, **kw):
        return deployed.parse(doc, where=url)
    monkeypatch.setattr(deployed, "fetch", fake_fetch)


def test_verify_against_a_matching_deployment(project, monkeypatch,
                                              capsys):
    main(["lock"])
    lock = json.loads((project / "promptlock.lock").read_text())
    live = {row["id"]: row["hash"] for row in lock["prompts"]}
    _serve(monkeypatch, {"canon_scheme": canon.SCHEME,
                         "prompts": live})
    assert main(["verify", "--deployed", "http://svc/_promptlock"]) == 0


def test_verify_catches_a_stale_deployment(project, monkeypatch,
                                           capsys):
    main(["lock"])
    lock = json.loads((project / "promptlock.lock").read_text())
    live = {row["id"]: row["hash"] for row in lock["prompts"]}
    live["triage"] = "sha256:" + "1" * 64
    _serve(monkeypatch, {"canon_scheme": canon.SCHEME,
                         "prompts": live})
    assert main(["verify", "--deployed", "http://svc/_promptlock"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out


def test_a_prompt_the_deployment_does_not_report(project, monkeypatch,
                                                 capsys):
    main(["lock"])
    lock = json.loads((project / "promptlock.lock").read_text())
    live = {row["id"]: row["hash"] for row in lock["prompts"]
            if row["id"] != "digest"}
    _serve(monkeypatch, {"canon_scheme": canon.SCHEME,
                         "prompts": live})
    assert main(["verify", "--deployed", "http://svc/x"]) == 1
    assert "not reported by the deployment" in capsys.readouterr().out


def test_a_running_prompt_nobody_pinned(project, monkeypatch, capsys):
    main(["lock"])
    lock = json.loads((project / "promptlock.lock").read_text())
    live = {row["id"]: row["hash"] for row in lock["prompts"]}
    live["undeclared"] = "sha256:" + "2" * 64
    _serve(monkeypatch, {"canon_scheme": canon.SCHEME,
                         "prompts": live})
    assert main(["verify", "--deployed", "http://svc/x"]) == 1
    assert "running, not in the lockfile" in capsys.readouterr().out


def test_a_scheme_mismatch_refuses_rather_than_reporting_drift(
        project, monkeypatch, capsys):
    main(["lock"])
    _serve(monkeypatch, {"canon_scheme": 1,
                         "prompts": {"triage": "sha256:" + "3" * 64}})
    assert main(["verify", "--deployed", "http://svc/x"]) == 2
    assert "not comparable" in capsys.readouterr().err
