from promptlock.commands.main import main


def test_fmt_strips_trailing_whitespace(project):
    p = project / "prompts" / "triage.md"
    p.write_text("Classify.   \n\n{{ticket}}\n", encoding="utf-8")
    assert main(["fmt"]) == 0
    assert p.read_text() == "Classify.\n\n{{ticket}}\n"


def test_fmt_does_not_change_the_hash(project):
    main(["lock"])
    p = project / "prompts" / "triage.md"
    p.write_text("Classify.   \n\n{{ticket}}\n", encoding="utf-8")
    main(["fmt"])
    assert main(["verify"]) == 0


def test_fmt_check_changes_nothing(project):
    p = project / "prompts" / "triage.md"
    before = "Classify.   \n\n{{ticket}}\n"
    p.write_text(before, encoding="utf-8")
    assert main(["fmt", "--check"]) == 1
    assert p.read_text() == before


def test_fmt_check_is_clean_on_clean_files(project):
    assert main(["fmt", "--check"]) == 0


def test_fmt_does_not_rewrap(project):
    p = project / "prompts" / "triage.md"
    text = ("A very long single line that a prose formatter would be "
            "sorely tempted to wrap at some column or other.\n")
    p.write_text(text, encoding="utf-8")
    main(["fmt"])
    assert p.read_text() == text


def test_fmt_writes_lf(project):
    p = project / "prompts" / "triage.md"
    p.write_bytes(b"Classify.\r\n\r\n{{ticket}}\r\n")
    main(["fmt"])
    assert b"\r\n" not in p.read_bytes()
