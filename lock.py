"""Print a stable hash of a prompt file."""
import argparse
import hashlib
import sys


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    for p in args.paths:
        with open(p, encoding="utf-8") as fh:
            print(digest(fh.read()), p)


if __name__ == "__main__":
    sys.exit(main())
