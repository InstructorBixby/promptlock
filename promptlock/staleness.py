"""Is an eval result still about the prompt that is pinned now.

Three states, and the middle one is the whole point:

  current   the result's prompt hash is the pinned hash
  stale     the result's prompt hash is NOT the pinned hash
  missing   the prompt has no result for this suite at all

`stale` is not a bug and not a failure of the eval. It is a fact about
attribution: that number describes a text that is no longer deployed.
The failure mode this prevents is a report citing last quarter's
injection rate for a prompt that was rewritten in between, which is the
single most common way these numbers end up false.
"""
from __future__ import annotations

from dataclasses import dataclass

CURRENT = "current"
STALE = "stale"
MISSING = "missing"


@dataclass
class Status:
    prompt: str
    suite: str
    state: str
    pinned_hash: str = ""
    result_hash: str = ""
    recorded: str = ""

    def __str__(self) -> str:
        if self.state == MISSING:
            return f"{MISSING:8} {self.prompt}: no result for {self.suite}"
        if self.state == STALE:
            return (f"{STALE:8} {self.prompt} / {self.suite}: measured "
                    f"against {self.result_hash[7:19]}, pinned is "
                    f"{self.pinned_hash[7:19]}")
        return f"{CURRENT:8} {self.prompt} / {self.suite}"


def assess(pinned: dict, records: dict, suites=()) -> list[Status]:
    """`pinned` is id -> Pin; `records` is (prompt, suite) -> Record."""
    out = []
    seen_suites = {suite for _, suite in records} | set(suites)
    for pid, pin in sorted(pinned.items()):
        relevant = [s for s in sorted(seen_suites)
                    if (pid, s) in records] or sorted(seen_suites)
        for suite in relevant:
            rec = records.get((pid, suite))
            if rec is None:
                out.append(Status(pid, suite, MISSING,
                                  pinned_hash=pin.hash))
            elif rec.prompt_hash != pin.hash:
                out.append(Status(pid, suite, STALE,
                                  pinned_hash=pin.hash,
                                  result_hash=rec.prompt_hash,
                                  recorded=rec.recorded))
            else:
                out.append(Status(pid, suite, CURRENT,
                                  pinned_hash=pin.hash,
                                  result_hash=rec.prompt_hash,
                                  recorded=rec.recorded))
    return out
