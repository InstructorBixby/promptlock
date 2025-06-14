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
    assert template.render("{{x}}-{{x}}", {"x": "7"}) == "7-7"


def test_missing_is_an_error():
    with pytest.raises(template.MissingVariable) as e:
        template.render("hi {{who}}", {})
    assert "who" in str(e.value)


def test_unknown_is_an_error():
    with pytest.raises(template.UnknownVariable) as e:
        template.render("hi", {"who": "you"})
    assert "who" in str(e.value)


def test_a_substituted_value_is_not_re_scanned():
    assert template.render("{{a}}", {"a": "{{b}}"}) == "{{b}}"


# --- the escape -----------------------------------------------------

def test_escaped_placeholder_is_not_a_variable():
    assert template.variables("example: {{{{name}}}}") == []


def test_escaped_placeholder_renders_as_literal_braces():
    out = template.render("example: {{{{name}}}}", {})
    assert out == "example: {{name}}"


def test_escaped_and_real_in_one_template():
    text = "Fill {{{{slot}}}} using {{value}}"
    assert template.variables(text) == ["value"]
    assert template.render(text, {"value": "7"}) == "Fill {{slot}} using 7"


# --- suspicious shapes ----------------------------------------------

def test_unclosed_placeholder_is_suspicious():
    assert template.suspicious("hi {{who\n") == ["{{who"]


def test_hyphenated_name_is_suspicious_not_a_variable():
    assert template.variables("{{first-name}}") == []
    assert template.suspicious("{{first-name}}") == ["{{first-name}}"]


def test_a_real_placeholder_is_not_suspicious():
    assert template.suspicious("{{who}}") == []


def test_an_escaped_placeholder_is_not_suspicious():
    assert template.suspicious("{{{{who}}}}") == []
