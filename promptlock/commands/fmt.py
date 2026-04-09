"""`promptlock fmt`: make the file agree with its own hash.

The hash is over a canonical form, so a file with trailing whitespace
in it hashes as though it did not have any. `fmt` removes that gap by
writing back the parts of the canonical form that are unambiguously
editor artefacts.

It does NOT normalise Unicode, even though the hash does. See
docs/unicode.md: a prompt can mean the exact sequence it contains, and
a formatter that rewrites codepoints is a formatter that edits a
production instruction without being asked.

It only touches prompts that are files. A source is a read-only
interface by design and `fmt` is the only thing in here that writes, so
source-backed prompts are skipped and said to be skipped.
"""
from __future__ import annotations

from promptlock import canon, registry


def run(args) -> int:
    reg = registry.load(args.registry)
    changed, skipped = [], []
    for entry in reg:
        if entry.source:
            skipped.append(entry.id)
            continue
        text = reg.read(entry)
        target = canon.formatted(text)
        if not canon.is_nfc(text):
            print(f"{entry.id}: not in NFC; leaving the sequence alone "
                  f"(the hash folds it, this file does not)")
        if target == text:
            continue
        changed.append(entry.id)
        if not args.check:
            (reg.root / entry.path).write_text(
                target, encoding="utf-8", newline="\n")
    for pid in skipped:
        print(f"{pid}: skipped, not a file")
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
