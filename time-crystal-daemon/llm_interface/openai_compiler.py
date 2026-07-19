#!/usr/bin/env python3
"""Optional OpenAI-backed intent compiler for the Time Crystal Daemon.

Drop-in replacement for the rule-based compiler in llm_sidecar.py.
The model is used strictly as a *compiler*: its only job is to emit a JSON
command plan, which is then validated against the IDL schema before anything
touches the daemon. Invalid or privilege-escalating plans are rejected.

NOTE: This module makes no network calls unless you explicitly construct
OpenAICompiler with an API key configured in your environment and call
compile(). Nothing in the bundled tooling invokes it automatically.
"""

from __future__ import annotations

import json
import os

IDL_SCHEMA: dict[str, dict] = {
    "get_status": {"level": "technician", "params": set()},
    "list_modules": {"level": "technician", "params": set()},
    "get_module": {"level": "technician", "params": {"module_id"}},
    "diagnose": {"level": "technician", "params": {"scope", "target"}},
    "trace_atom": {"level": "technician", "params": {"handle", "name"}},
    "get_tc_hierarchy": {"level": "technician", "params": set()},
    "explain_decision": {"level": "technician", "params": {"decision_id"}},
    "pause_module": {"level": "engineer", "params": {"module_id"}},
    "resume_module": {"level": "engineer", "params": {"module_id"}},
    "set_attention": {"level": "engineer", "params": {"module_id", "value"}},
    "inject_atom": {"level": "engineer", "params": {"name", "type", "tv", "out"}},
    "set_tc_phase": {"level": "engineer", "params": {"level", "offset_us"}},
}

SYSTEM_PROMPT = """You compile user intent into IDL commands for a time \
crystal daemon. Respond ONLY with a JSON array of objects, each having \
"method" and "params". Available methods and params:
""" + json.dumps({k: sorted(v["params"]) for k, v in IDL_SCHEMA.items()}, indent=2)


class PlanValidationError(ValueError):
    pass


def validate_plan(plan: object, access_level: str) -> list[dict]:
    """Validate a candidate plan against the IDL schema and access level."""
    if not isinstance(plan, list):
        raise PlanValidationError("plan must be a JSON array")
    out: list[dict] = []
    for i, cmd in enumerate(plan):
        if not isinstance(cmd, dict):
            raise PlanValidationError(f"command #{i} is not an object")
        method = cmd.get("method")
        if method not in IDL_SCHEMA:
            raise PlanValidationError(f"command #{i}: unknown method {method!r}")
        spec = IDL_SCHEMA[method]
        if spec["level"] == "engineer" and access_level != "engineer":
            raise PlanValidationError(
                f"command #{i}: {method} requires engineer access")
        params = cmd.get("params") or {}
        unknown = set(params) - spec["params"]
        if unknown:
            raise PlanValidationError(
                f"command #{i}: unknown params {sorted(unknown)}")
        out.append({"method": method, "params": params})
    return out


class OpenAICompiler:
    """Compile natural language to a validated IDL plan via an OpenAI model."""

    def __init__(self, model: str = "gpt-4.1-mini"):
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set; use the rule-based compiler in "
                "llm_sidecar.py, or export a key to opt in to model-backed "
                "compilation.")
        from openai import OpenAI  # deferred import; optional dependency
        self._client = OpenAI()
        self._model = model

    def compile(self, text: str, access_level: str = "technician") -> list[dict]:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": text}],
            temperature=0,
        )
        raw = resp.choices[0].message.content or "[]"
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        return validate_plan(json.loads(raw), access_level)
