"""Read the prompt hashes a running service says it is using.

This is the check that actually matters and it needs something from the
application: an endpoint that reports, for each prompt id, the hash of
the text it currently has loaded. Four lines of application code using
`promptlock.canon`, and in exchange the gate stops being a statement
about a git checkout.

    GET /_promptlock
    {"canon_scheme": 2,
     "prompts": {"support_triage": "sha256:9f2c..."}}

Deliberately hashes, not text. The service does not have to expose its
prompts to the CI runner to be audited, which removes the main reason
anyone refuses to add the endpoint.

urllib rather than a dependency: this is the only HTTP in the project
and it is one GET.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request


class DeployedError(Exception):
    pass


def fetch(url: str, *, timeout: float = 10.0,
          headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {},
                                 method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise DeployedError(f"{url}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DeployedError(f"{url}: {exc}") from exc
    try:
        doc = json.loads(body)
    except json.JSONDecodeError as exc:
        raise DeployedError(f"{url}: response is not JSON") from exc
    return parse(doc, where=url)


def parse(doc: dict, *, where: str = "response") -> dict:
    if not isinstance(doc, dict) or "prompts" not in doc:
        raise DeployedError(f"{where}: no 'prompts' object")
    prompts = doc["prompts"]
    if not isinstance(prompts, dict):
        raise DeployedError(f"{where}: 'prompts' is not an object")
    out = {}
    for pid, h in prompts.items():
        if not isinstance(h, str) or not h.startswith("sha256:"):
            raise DeployedError(
                f"{where}: {pid} reports {h!r}, not a sha256: digest")
        out[pid] = h
    scheme = doc.get("canon_scheme")
    return {"prompts": out, "canon_scheme": scheme}
