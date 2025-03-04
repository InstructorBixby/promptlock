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


def digest(text):
    return hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    for p in args.paths:
        with open(p, encoding="utf-8") as fh:
            print(digest(fh.read()), p)


if __name__ == "__main__":
    sys.exit(main())
