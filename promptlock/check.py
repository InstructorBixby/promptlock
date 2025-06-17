"""Static checks over the registry, independent of the lockfile.

`verify` answers "has the text changed". These answer "is the
declaration true", which is a different failure and shows up earlier:
a prompt whose declared variables have drifted from its placeholders
will render with a silent empty string at every call site that trusts
the declaration.
"""
from __future__ import annotations

from dataclasses import dataclass

from promptlock import registry, template


@dataclass
class Problem:
    id: str
    kind: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind:14} {self.id}: {self.detail}"


def check(reg: registry.Registry) -> list[Problem]:
    out = []
    for entry in reg:
        text = reg.read(entry)
        found = template.variables(text)
        declared = list(entry.variables) + list(entry.optional)

        for name in found:
            if name not in declared:
                out.append(Problem(entry.id, "undeclared",
                                   f"{{{{{name}}}}} is in the text but "
                                   f"not in variables"))
        for name in declared:
            if name not in found:
                out.append(Problem(entry.id, "unused",
                                   f"declared {name}, no placeholder "
                                   f"in the text"))
        for name in sorted(set(entry.variables) & set(entry.optional)):
            out.append(Problem(entry.id, "contradictory",
                               f"{name} is both required and optional"))
        for frag in template.suspicious(text):
            out.append(Problem(entry.id, "suspicious",
                               f"{frag!r} looks like a placeholder and "
                               f"will not be substituted; escape it as "
                               f"{{{{{{{{...}}}}}}}} if it is literal"))
        if not entry.owner:
            out.append(Problem(entry.id, "no-owner",
                               "no owner; nobody to ask about a change"))
    return out
