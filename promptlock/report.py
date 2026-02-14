"""One structure for what verify found, rendered two ways.

CI wants an exit code, a human wants lines, and something upstream
eventually wants JSON. Building the JSON from the same objects the human
output comes from is the only way those three stay consistent.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

OK = "ok"
DRIFT = "drift"
UNPINNED = "unpinned"
MISSING = "missing"
MOVED = "moved"
UNKNOWN = "unknown"

FAILING = {DRIFT, UNPINNED, MISSING, UNKNOWN}


@dataclass
class Item:
    id: str
    state: str
    pinned_hash: str = ""
    found_hash: str = ""
    pinned_path: str = ""
    found_path: str = ""
    detail: str = ""

    @property
    def failing(self) -> bool:
        return self.state in FAILING


@dataclass
class Report:
    items: list = field(default_factory=list)
    signature: str = ""

    @property
    def failures(self) -> list:
        return [i for i in self.items if i.failing]

    def to_json(self) -> dict:
        return {
            "ok": not self.failures,
            "signature": self.signature,
            "counts": {
                state: sum(1 for i in self.items if i.state == state)
                for state in (OK, DRIFT, UNPINNED, MISSING, MOVED,
                              UNKNOWN)
            },
            "items": [asdict(i) for i in self.items],
        }

    def lines(self, verbose: bool = False) -> list[str]:
        out = []
        for item in self.items:
            if item.state == OK and not verbose:
                continue
            out.append(f"{item.state.upper():8} {item.id}: "
                       f"{item.detail}")
        return out
