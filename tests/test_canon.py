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


def test_crlf_folds_under_scheme_2():
    assert h("a\r\nb\n") == h("a\nb\n")


def test_lone_cr_folds_too():
    assert h("a\rb\n") == h("a\nb\n")


def test_nfc_folds():
    precomposed = "caf\u00e9\n"
    decomposed = "cafe\u0301\n"
    assert precomposed != decomposed
    assert h(precomposed) == h(decomposed)


def test_normalisation_does_not_fold_a_zero_width_character():
    # NFC is not a confusable filter and must not be mistaken for one.
    assert h("ab\n") != h("a\u200bb\n")


def test_digest_is_prefixed():
    assert h("x\n").startswith("sha256:")


def test_short_is_twelve_hex():
    d = h("x\n")
    assert len(canon.short(d)) == 12
    assert canon.short(d) in d


def test_scheme_is_two():
    assert canon.SCHEME == 2


def test_clean_text_reports_nothing_lossy():
    assert canon.lossy("hello\nworld\n") == []


def test_lossy_names_the_trailing_whitespace():
    assert any("trailing whitespace" in n
               for n in canon.lossy("hello \nworld\n"))


def test_lossy_names_the_added_newline():
    assert any("final newline" in n for n in canon.lossy("hello"))


def test_lossy_names_carriage_returns():
    assert any("carriage return" in n for n in canon.lossy("a\r\nb\n"))


def test_lossy_names_a_decomposed_sequence():
    notes = canon.lossy("cafe\u0301\n")
    assert any("not in NFC" in n for n in notes)
