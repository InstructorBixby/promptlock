from promptlock.commands.main import main


def test_cached_lock_is_identical(project):
    main(["lock"])
    plain = (project / "promptlock.lock").read_text()
    (project / "promptlock.lock").unlink()
    main(["--cache", "lock"])
    assert (project / "promptlock.lock").read_text() == plain


def test_the_cache_file_lands_under_promptlock(project):
    main(["--cache", "lock"])
    assert (project / ".promptlock" / "cache" / "hashes.json").exists()


def test_verify_ignores_the_cache(project, capsys):
    main(["--cache", "lock"])
    (project / "prompts" / "triage.md").write_text(
        "Classify it.\n\n{{ticket}}\n", encoding="utf-8")
    assert main(["--cache", "verify"]) == 1
    assert "DRIFT    triage" in capsys.readouterr().out
