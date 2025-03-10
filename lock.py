"""Print a stable hash of a prompt file."""
import argparse
import hashlib
import sys

BOM = "\ufeff"


def canonical(text):
    """Canonical form, scheme 1.

    Line endings are deliberately NOT normalised: see NOTES.md.
    """
    if text.startswith(BOM):
        text = text[1:]
    lines = [ln.rstrip(" \t") for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def lossy(text):
    """What canonicalisation threw away.

    Usually nothing anyone cares about. Occasionally it is the whole
    point of the prompt -- a trailing space before the model's turn is
    a real tokenisation decision in some templates -- so the one thing
    this must not do is throw it away quietly.
    """
    notes = []
    if text.startswith(BOM):
        notes.append("leading byte-order mark stripped")
    body = text[1:] if text.startswith(BOM) else text
    if any(ln != ln.rstrip(" \t") for ln in body.split("\n")[:-1]):
        notes.append("trailing whitespace stripped from one or more lines")
    if body and not body.endswith("\n"):
        notes.append("final newline added")
    if body.endswith("\n\n"):
        notes.append("repeated final newlines collapsed to one")
    return notes


def digest(text):
    return hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    for p in args.paths:
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        print(digest(text), p)
        if not args.quiet:
            for note in lossy(text):
                print(f"  note: {note}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
