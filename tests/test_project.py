from promptlock import canon
from promptlock.project import Project


def test_lock_stores_every_text(project):
    proj = Project.open()
    for pin in proj.lock():
        assert proj.store.has(pin.hash)


def test_stored_text_is_the_raw_text(project):
    (project / "prompts" / "triage.md").write_text(
        "Classify.   \n\n{{ticket}}\n", encoding="utf-8")
    proj = Project.open()
    proj.lock()
    d = canon.digest("Classify.\n\n{{ticket}}\n")
    assert proj.store.get(d) == "Classify.   \n\n{{ticket}}\n"


def test_locking_twice_is_idempotent(project):
    first = Project.open().lock()
    second = Project.open().lock()
    assert [p.hash for p in first] == [p.hash for p in second]


def test_an_edit_keeps_the_old_object(project):
    old = {p.id: p.hash for p in Project.open().lock()}
    (project / "prompts" / "triage.md").write_text(
        "Classify, briefly.\n\n{{ticket}}\n", encoding="utf-8")
    proj = Project.open()
    proj.lock()
    assert proj.store.has(old["triage"])
