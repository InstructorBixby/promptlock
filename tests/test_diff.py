from promptlock import diff


def test_identical():
    assert diff.classify("a b\n", "a b\n") == diff.IDENTICAL


def test_canonically_identical_is_identical():
    assert diff.classify("a b   \n", "a b\n") == diff.IDENTICAL


def test_reflow_is_whitespace_only():
    a = "be brief and\nprecise\n"
    b = "be brief\nand precise\n"
    assert diff.classify(a, b) == diff.WHITESPACE_ONLY


def test_a_changed_word_is_substantive():
    assert diff.classify("be brief\n", "be terse\n") == diff.SUBSTANTIVE


def test_an_added_word_is_substantive():
    assert (diff.classify("be brief\n", "be very brief\n")
            == diff.SUBSTANTIVE)


def test_whitespace_only_still_moves_the_hash():
    from promptlock import canon
    a, b = "be brief and\nprecise\n", "be brief\nand precise\n"
    assert canon.digest(a) != canon.digest(b)
    assert diff.classify(a, b) == diff.WHITESPACE_ONLY


def test_spans_merge_adjacent_runs():
    spans = diff.word_spans("a b c d", "a x y d")
    ops = [s.op for s in spans]
    assert ops == ["same", "del", "add", "same"]
    assert spans[1].text == "b c"
    assert spans[2].text == "x y"


def test_counts():
    assert diff.changed_word_count("a b c", "a c") == (0, 1)
    assert diff.changed_word_count("a c", "a b c") == (1, 0)


def test_empty_against_something():
    assert diff.classify("", "hello\n") == diff.SUBSTANTIVE
