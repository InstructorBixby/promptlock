from promptlock import check, registry


def build(tmp_path, toml, text):
    (tmp_path / "promptlock.toml").write_text(toml, encoding="utf-8")
    (tmp_path / "a.md").write_text(text, encoding="utf-8")
    return registry.load(tmp_path / "promptlock.toml")


GOOD = '[prompt.a]\npath = "a.md"\nowner = "me"\nvariables = ["x"]\n'


def test_clean(tmp_path):
    reg = build(tmp_path, GOOD, "hi {{x}}\n")
    assert check.check(reg) == []


def test_undeclared_placeholder(tmp_path):
    reg = build(tmp_path, GOOD, "hi {{x}} {{y}}\n")
    problems = check.check(reg)
    assert [p.kind for p in problems] == ["undeclared"]
    assert "y" in problems[0].detail


def test_declared_but_unused(tmp_path):
    toml = GOOD.replace('["x"]', '["x", "y"]')
    reg = build(tmp_path, toml, "hi {{x}}\n")
    assert [p.kind for p in check.check(reg)] == ["unused"]


def test_required_and_optional_at_once(tmp_path):
    toml = GOOD + 'optional = ["x"]\n'
    reg = build(tmp_path, toml, "hi {{x}}\n")
    assert any(p.kind == "contradictory" for p in check.check(reg))


def test_missing_owner(tmp_path):
    toml = '[prompt.a]\npath = "a.md"\nvariables = ["x"]\n'
    reg = build(tmp_path, toml, "hi {{x}}\n")
    assert any(p.kind == "no-owner" for p in check.check(reg))
