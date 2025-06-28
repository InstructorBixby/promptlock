from promptlock import render


T = "Classify this.\n\n{{body}}\n"


def test_render_hash_moves_when_a_variable_changes():
    a = render.render_hash(T, {"body": "one"})
    b = render.render_hash(T, {"body": "two"})
    assert a != b


def test_template_hash_does_not():
    h1 = render.hashes(T, {"body": "one"})
    h2 = render.hashes(T, {"body": "two"})
    assert h1["template"] == h2["template"]
    assert h1["render"] != h2["render"]


def test_variables_hash_is_key_order_independent():
    a = render.variables_hash({"a": 1, "b": 2})
    b = render.variables_hash({"b": 2, "a": 1})
    assert a == b


def test_variables_hash_canonicalises_each_value():
    a = render.variables_hash({"x": "hello  \n"})
    b = render.variables_hash({"x": "hello\n"})
    assert a == b


def test_variables_hash_distinguishes_key_from_value():
    # "ab" -> "" and "a" -> "b" must not collide.
    assert (render.variables_hash({"ab": ""})
            != render.variables_hash({"a": "b"}))


def test_non_ascii_survives():
    h = render.variables_hash({"x": "na\u00efve caf\u00e9"})
    assert h.startswith("sha256:")
