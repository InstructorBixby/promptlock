from promptlock import diffrender


def test_inline_marks_a_substitution():
    out = diffrender.inline("be brief", "be terse")
    assert "[-brief-]" in out
    assert "[+terse+]" in out


def test_inline_keeps_unchanged_words_bare():
    out = diffrender.inline("be brief now", "be terse now")
    assert out.startswith("be ")
    assert "now" in out


def test_summary_names_whitespace_only():
    a, b = "be brief and\nprecise\n", "be brief\nand precise\n"
    assert "whitespace only" in diffrender.summary(a, b)


def test_summary_counts_substantive_words():
    s = diffrender.summary("be brief", "be very brief")
    assert "+1 word" in s


def test_summary_for_identical():
    assert "identical" in diffrender.summary("a\n", "a   \n")
