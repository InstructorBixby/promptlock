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


def test_fmt_leaves_a_decomposed_sequence_alone(project, capsys):
    # The probe prompt means the exact sequence it contains.
    p = project / "prompts" / "triage.md"
    text = "Classify cafe\u0301.\n\n{{ticket}}\n"
    p.write_text(text, encoding="utf-8")
    assert main(["fmt"]) == 0
    assert p.read_text() == text
    assert "not in NFC" in capsys.readouterr().out


def test_fmt_fixes_layout_without_touching_the_sequence(project):
    p = project / "prompts" / "triage.md"
    p.write_text("Classify cafe\u0301.   \n\n{{ticket}}\n",
                 encoding="utf-8")
    main(["fmt"])
    assert p.read_text() == "Classify cafe\u0301.\n\n{{ticket}}\n"
