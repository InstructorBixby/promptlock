"""`promptlock diff`: compare two versions of one prompt.

Either side can be a lockfile pin, an explicit digest, a file, or the
working copy. The common case -- "what changed since the pin" -- is the
default with no arguments beyond the id.
"""
from __future__ import annotations

import sys
from pathlib import Path

from promptlock import canon, diff, diffrender, project, store


def resolve(proj: project.Project, pid: str, ref: str | None) -> str:
    """A ref is 'pinned', 'working', a digest, or a path."""
    if ref in (None, "pinned"):
        pin = proj.pinned().get(pid)
        if pin is None:
            raise store.StoreError(f"{pid} is not in the lockfile")
        return proj.text_for(pin.hash)
    if ref == "working":
        return proj.registry.read(proj.registry.entries[pid])
    if ref.startswith("sha256:"):
        return proj.text_for(ref)
    if len(ref) == 12 and all(c in "0123456789abcdef" for c in ref):
        for pin in proj.pinned().values():
            if canon.short(pin.hash) == ref:
                return proj.text_for(pin.hash)
        raise store.StoreError(f"no pin with short hash {ref}")
    p = Path(ref)
    if p.exists():
        return p.read_text(encoding="utf-8")
    raise store.StoreError(f"cannot resolve {ref!r}")


def run(args) -> int:
    proj = project.Project.open(args.registry, args.lock)
    if args.id not in proj.registry.entries:
        print(f"promptlock: no prompt {args.id!r}", file=sys.stderr)
        return 2
    before = resolve(proj, args.id, args.from_ref)
    after = resolve(proj, args.id, args.to_ref)

    kind = diff.classify(before, after)
    print(f"{args.id}: {canon.short(canon.digest(before))} -> "
          f"{canon.short(canon.digest(after))}")
    print(diffrender.summary(before, after))
    if kind != diff.IDENTICAL:
        print()
        if kind == diff.WHITESPACE_ONLY:
            print("(no word-level changes to show)")
        else:
            sys.stdout.write(diffrender.inline(before, after))
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("diff", help="compare two versions of a prompt")
    p.add_argument("id")
    p.add_argument("--from", dest="from_ref", default="pinned",
                   metavar="REF",
                   help="pinned (default), working, a digest, or a path")
    p.add_argument("--to", dest="to_ref", default="working",
                   metavar="REF")
    p.set_defaults(fn=run)
