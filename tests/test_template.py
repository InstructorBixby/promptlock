import pytest

from promptlock import template


def test_extracts_in_order():
    assert template.variables("{{b}} then {{a}}") == ["b", "a"]


def test_deduplicates():
    assert template.variables("{{a}} {{a}}") == ["a"]


def test_allows_inner_whitespace():
    assert template.variables("{{ a }}") == ["a"]


def test_single_braces_are_literal():
    text = 'Reply as {"category": "..."}'
    assert template.variables(text) == []
    assert template.render(text, {}) == text


def test_renders():
    assert template.render("hi {{who}}", {"who": "you"}) == "hi you"


def test_renders_a_repeated_placeholder_everywhere():
    out = template.render("{{x}}-{{x}}", {"x": "7"})
    assert out == "7-7"


def test_missing_is_an_error():
    with pytest.raises(template.MissingVariable) as e:
        template.render("hi {{who}}", {})
    assert "who" in str(e.value)


def test_unknown_is_an_error():
    with pytest.raises(template.UnknownVariable) as e:
        template.render("hi", {"who": "you"})
    assert "who" in str(e.value)


def test_a_substituted_value_is_not_re_scanned():
    # Otherwise a value containing a placeholder is an injection into
    # the template itself.
    out = template.render("{{a}}", {"a": "{{b}}"})
    assert out == "{{b}}"
