"""`promptlock hash`: hash files with no registry involved."""
from __future__ import annotations

from promptlock import canon


def run(args) -> int:
    for path in args.paths:
        with open(path, encoding="utf-8") as fh:
            print(canon.digest(fh.read()), path)
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("hash", help="hash files, ignoring the registry")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=run)
