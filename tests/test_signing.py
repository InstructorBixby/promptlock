import pytest

from promptlock import signing


class FakeProc:
    def __init__(self, rc=0, err=""):
        self.returncode = rc
        self.stderr = err
        self.stdout = ""


def test_missing_cosign_is_a_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(signing.shutil, "which", lambda _: None)
    with pytest.raises(signing.SigningError) as e:
        signing.sign(tmp_path / "promptlock.lock", key="k")
    assert "not on PATH" in str(e.value)


def test_sign_writes_beside_the_lockfile(tmp_path, monkeypatch):
    lock = tmp_path / "promptlock.lock"
    lock.write_text("{}\n")
    monkeypatch.setattr(signing.shutil, "which", lambda _: "/bin/cosign")
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        return FakeProc()

    monkeypatch.setattr(signing.subprocess, "run", fake_run)
    sig = signing.sign(lock, key="cosign.key")
    assert sig.name == "promptlock.lock.sig"
    assert "sign-blob" in seen["cmd"]


def test_a_failing_cosign_is_reported(tmp_path, monkeypatch):
    lock = tmp_path / "promptlock.lock"
    lock.write_text("{}\n")
    monkeypatch.setattr(signing.shutil, "which", lambda _: "/bin/cosign")
    monkeypatch.setattr(signing.subprocess, "run",
                        lambda *a, **k: FakeProc(1, "bad key"))
    with pytest.raises(signing.SigningError) as e:
        signing.sign(lock, key="k")
    assert "bad key" in str(e.value)


def test_verify_needs_a_signature_file(tmp_path, monkeypatch):
    lock = tmp_path / "promptlock.lock"
    lock.write_text("{}\n")
    monkeypatch.setattr(signing.shutil, "which", lambda _: "/bin/cosign")
    with pytest.raises(signing.SigningError) as e:
        signing.verify(lock, key="k")
    assert "no signature" in str(e.value)


def test_verify_passes_on_a_good_signature(tmp_path, monkeypatch):
    lock = tmp_path / "promptlock.lock"
    lock.write_text("{}\n")
    (tmp_path / "promptlock.lock.sig").write_text("sig")
    monkeypatch.setattr(signing.shutil, "which", lambda _: "/bin/cosign")
    monkeypatch.setattr(signing.subprocess, "run",
                        lambda *a, **k: FakeProc())
    signing.verify(lock, key="k")
