import lock


def test_trailing_space_is_not_content():
    assert lock.digest("hello   \nworld\n") == lock.digest("hello\nworld\n")


def test_missing_final_newline_is_not_content():
    assert lock.digest("hello") == lock.digest("hello\n")


def test_many_final_newlines_collapse():
    assert lock.digest("hello\n\n\n\n") == lock.digest("hello\n")


def test_bom_is_stripped():
    assert lock.digest("\ufeffhello\n") == lock.digest("hello\n")


def test_interior_blank_lines_are_content():
    assert lock.digest("a\n\nb\n") != lock.digest("a\nb\n")


def test_crlf_is_content_for_now():
    # Deliberate, and recorded in NOTES.md. If this test ever flips it
    # is a canon scheme bump, not a bug fix.
    assert lock.digest("a\r\nb\n") != lock.digest("a\nb\n")
