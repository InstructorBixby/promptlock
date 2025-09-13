"""Argument parsing and dispatch.

Exit codes, because the only interesting caller is CI:

  0  everything matched
  1  drift, a failed check, or a stale eval binding
  2  usage or configuration error
"""
from __future__ import annotations

import argparse
import sys

from promptlock import evals as evals_mod
from promptlock import lockfile, registry, store
from promptlock.commands import diff as diff_cmd
from promptlock.commands import evals as evals_cmd
from promptlock.commands import hash as hash_cmd
from promptlock.commands import lock as lock_cmd
from promptlock.commands import render as render_cmd
from promptlock.commands import verify as verify_cmd

MODULES = (lock_cmd, verify_cmd, diff_cmd, render_cmd, evals_cmd,
           hash_cmd)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="promptlock")
    ap.add_argument("--registry", default="promptlock.toml")
    ap.add_argument("--lock", default="promptlock.lock")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for mod in MODULES:
        mod.add_parser(sub)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (registry.RegistryError, lockfile.LockError,
            store.StoreError, evals_mod.EvalError) as exc:
        print(f"promptlock: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
