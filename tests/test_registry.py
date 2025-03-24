import pytest

from promptlock import registry


def write(tmp_path, body, **files):
    (tmp_path / "promptlock.toml").write_text(body, encoding="utf-8")
    for name, text in files.items():
        p = tmp_path / name.replace("__", "/")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path / "promptlock.toml"


BASIC = """\
[prompt.a]
path = "prompts/a.md"
owner = "me"
variables = ["x"]
"""


def test_loads_an_entry(tmp_path):
    p = write(tmp_path, BASIC, prompts__a__md="hi {{x}}\n")
    reg = registry.load(p)
    assert reg.entries["a"].owner == "me"
    assert reg.entries["a"].variables == ["x"]


def test_reads_the_text(tmp_path):
    p = write(tmp_path, BASIC, prompts__a__md="hi {{x}}\n")
    reg = registry.load(p)
    assert reg.read(reg.entries["a"]) == "hi {{x}}\n"


def test_iteration_is_sorted_by_id(tmp_path):
    body = BASIC + '\n[prompt.A0]\npath = "prompts/a.md"\n'
    p = write(tmp_path, body, prompts__a__md="hi\n")
    assert [e.id for e in registry.load(p)] == ["A0", "a"]


def test_unknown_key_is_an_error(tmp_path):
    body = '[prompt.a]\npath = "a.md"\nvaraibles = ["x"]\n'
    p = write(tmp_path, body, a__md="hi\n")
    with pytest.raises(registry.RegistryError) as e:
        registry.load(p)
    assert "varaibles" in str(e.value)


def test_missing_path_is_an_error(tmp_path):
    p = write(tmp_path, '[prompt.a]\nowner = "me"\n')
    with pytest.raises(registry.RegistryError):
        registry.load(p)


def test_empty_registry_is_an_error(tmp_path):
    p = write(tmp_path, "# nothing here\n")
    with pytest.raises(registry.RegistryError):
        registry.load(p)


def test_missing_file_is_an_error_at_read_time(tmp_path):
    p = write(tmp_path, BASIC)
    reg = registry.load(p)
    with pytest.raises(registry.RegistryError):
        reg.read(reg.entries["a"])
