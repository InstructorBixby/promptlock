"""Diff two prompt versions in a way that answers the real question.

A line diff of a prompt is nearly useless. Prompts are wrapped prose;
inserting one word reflows a paragraph and the line diff shows four
lines changed, which tells you nothing about whether the instruction
changed.

The other half of the problem is whitespace. Reflowing a paragraph,
converting tabs, or moving the final newline all change the hash --
correctly, the hash is over text -- but almost certainly do not change
behaviour. "The hash moved" and "the instructions moved" are different
facts and the reviewer needs to be told which one they are looking at.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from promptlock import canon

WORD_RE = re.compile(r"\S+")

IDENTICAL = "identical"
WHITESPACE_ONLY = "whitespace-only"
SUBSTANTIVE = "substantive"


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def classify(a: str, b: str) -> str:
    """Which of the three kinds of difference this is."""
    if canon.digest(a) == canon.digest(b):
        return IDENTICAL
    if words(a) == words(b):
        return WHITESPACE_ONLY
    return SUBSTANTIVE


@dataclass
class Span:
    op: str           # "same" | "add" | "del"
    words: list[str]

    @property
    def text(self) -> str:
        return " ".join(self.words)


def word_spans(a: str, b: str) -> list[Span]:
    """Word-level opcodes, adjacent runs merged."""
    wa, wb = words(a), words(b)
    sm = difflib.SequenceMatcher(a=wa, b=wb, autojunk=False)
    out: list[Span] = []

    def push(op, items):
        if not items:
            return
        if out and out[-1].op == op:
            out[-1].words.extend(items)
        else:
            out.append(Span(op, list(items)))

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            push("same", wa[i1:i2])
        elif tag == "delete":
            push("del", wa[i1:i2])
        elif tag == "insert":
            push("add", wb[j1:j2])
        else:
            push("del", wa[i1:i2])
            push("add", wb[j1:j2])
    return out


def changed_word_count(a: str, b: str) -> tuple[int, int]:
    spans = word_spans(a, b)
    added = sum(len(s.words) for s in spans if s.op == "add")
    removed = sum(len(s.words) for s in spans if s.op == "del")
    return added, removed
