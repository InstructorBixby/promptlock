"""`promptlock sign`: detached signature over the lockfile bytes."""
from __future__ import annotations

import sys

from promptlock import signing


def run(args) -> int:
    try:
        sig = signing.sign(args.lock, key=args.key,
                           sig_path=args.signature)
    except signing.SigningError as exc:
        print(f"promptlock: {exc}", file=sys.stderr)
        return 2
    print(f"signed {args.lock} -> {sig}")
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("sign", help="sign the lockfile with cosign")
    p.add_argument("--key", required=True)
    p.add_argument("--signature", default=None,
                   help="output path (default: <lockfile>.sig)")
    p.set_defaults(fn=run)
