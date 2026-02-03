"""Optional signing of the lockfile.

The lockfile is already a tamper-*detector* for prompt text: change the
text and the hash stops matching. It is not a tamper-detector for
itself. Someone who can edit the lockfile can re-pin a modified prompt
and `verify` will agree with them, because `verify`'s only question is
whether the text matches the pin.

A detached signature over the lockfile bytes closes that, to exactly
the extent that the verifying key is trustworthy -- which is the whole
question and is not one this module can answer. See docs/signing.md for
what this does and does not prove.

This shells out to cosign rather than reimplementing anything. A
signing scheme written by me, in here, would be the least reviewed code
in the project.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class SigningError(Exception):
    pass


def _cosign() -> str:
    exe = shutil.which("cosign")
    if not exe:
        raise SigningError(
            "cosign is not on PATH; signing is optional and this is "
            "the only thing that needs it")
    return exe


def sign(lock_path: str | Path, *, key: str,
         sig_path: str | Path | None = None) -> Path:
    lock = Path(lock_path)
    sig = Path(sig_path) if sig_path else lock.with_suffix(
        lock.suffix + ".sig")
    cmd = [_cosign(), "sign-blob", "--yes", "--key", key,
           "--output-signature", str(sig), str(lock)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SigningError(f"cosign sign-blob failed: "
                           f"{proc.stderr.strip() or proc.returncode}")
    return sig


def verify(lock_path: str | Path, *, key: str,
           sig_path: str | Path | None = None) -> None:
    """Raise SigningError unless the signature is good."""
    lock = Path(lock_path)
    sig = Path(sig_path) if sig_path else lock.with_suffix(
        lock.suffix + ".sig")
    if not sig.exists():
        raise SigningError(f"no signature at {sig}")
    cmd = [_cosign(), "verify-blob", "--key", key,
           "--signature", str(sig), str(lock)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SigningError(f"signature does not verify: "
                           f"{proc.stderr.strip() or proc.returncode}")
