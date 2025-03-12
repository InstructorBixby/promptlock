from promptlock import canon


def h(text):
    return canon.digest(text)


def test_trailing_space_is_not_content():
    assert h("hello   \nworld\n") == h("hello\nworld\n")


def test_missing_final_newline_is_not_content():
    assert h("hello") == h("hello\n")


def test_many_final_newlines_collapse():
    assert h("hello\n\n\n\n") == h("hello\n")


def test_bom_is_stripped():
    assert h("\ufeffhello\n") == h("hello\n")


def test_interior_blank_lines_are_content():
    assert h("a\n\nb\n") != h("a\nb\n")


def test_crlf_is_content_under_scheme_1():
    assert h("a\r\nb\n") != h("a\nb\n")


def test_digest_is_prefixed():
    assert h("x\n").startswith("sha256:")


def test_short_is_twelve_hex():
    d = h("x\n")
    assert len(canon.short(d)) == 12
    assert canon.short(d) in d


def test_clean_text_reports_nothing_lossy():
    assert canon.lossy("hello\nworld\n") == []


def test_lossy_names_the_trailing_whitespace():
    assert any("trailing whitespace" in n
               for n in canon.lossy("hello \nworld\n"))


def test_lossy_names_the_added_newline():
    assert any("final newline" in n for n in canon.lossy("hello"))
