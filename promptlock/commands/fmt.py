"""`promptlock fmt`: make the file agree with its own hash.

The hash is over a canonical form, so a file with trailing whitespace
in it hashes as though it did not have any. That is the intended
behaviour and it is also mildly unpleasant: the thing in the editor is
not the thing being hashed. `fmt` removes the gap by writing the
canonical form back.

Scoped deliberately narrowly. It touches whitespace, line endings and
the final newline, and it will not reorder, rewrap or rewrite a single
word. A formatter for prose is a formatter that silently edits a
production instruction.
"""
from __future__ import annotations

from promptlock import canon, registry


def run(args) -> int:
    reg = registry.load(args.registry)
    changed = []
    for entry in reg:
        text = reg.read(entry)
        formatted = canon.canonical(text)
        if formatted == text:
            continue
        changed.append(entry.id)
        if not args.check:
            (reg.root / entry.path).write_text(
                formatted, encoding="utf-8", newline="\n")
        for note in canon.lossy(text):
            print(f"{entry.id}: {note}")
    if args.check:
        for pid in changed:
            print(f"would reformat {pid}")
        print(f"{len(changed)} file(s) would change")
        return 1 if changed else 0
    print(f"reformatted {len(changed)} file(s)")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("fmt", help="write the canonical form back")
    p.add_argument("--check", action="store_true",
                   help="report, change nothing, exit 1 if any would")
    p.set_defaults(fn=run)
