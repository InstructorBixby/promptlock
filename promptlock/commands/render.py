"""`promptlock render`."""
from __future__ import annotations

import json
import sys

from promptlock import registry, render, template


def values_from(args) -> dict:
    values = {}
    if args.vars:
        with open(args.vars, encoding="utf-8") as fh:
            values = json.load(fh)
    for item in args.set or []:
        k, _, v = item.partition("=")
        values[k] = v
    return values


def run(args) -> int:
    reg = registry.load(args.registry)
    if args.id not in reg.entries:
        print(f"promptlock: no prompt {args.id!r}", file=sys.stderr)
        return 2
    text = reg.read(reg.entries[args.id])
    try:
        if args.hash:
            print(json.dumps(render.hashes(text, values_from(args)),
                             indent=1, sort_keys=True))
        else:
            sys.stdout.write(template.render(text, values_from(args)))
    except template.TemplateError as exc:
        print(f"promptlock: {args.id}: {exc}", file=sys.stderr)
        return 2
    return 0


def add_parser(sub) -> None:
    p = sub.add_parser("render", help="render a prompt with variables")
    p.add_argument("id")
    p.add_argument("--vars", help="JSON file of variable values")
    p.add_argument("--set", action="append", metavar="K=V")
    p.add_argument("--hash", action="store_true",
                   help="print the template, variables and render "
                        "hashes instead of the text")
    p.set_defaults(fn=run)
