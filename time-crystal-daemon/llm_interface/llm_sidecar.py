#!/usr/bin/env python3
"""LLM sidecar for the Time Crystal Daemon.

The sidecar is a *compiler, not an oracle*: it translates natural language
into explicit, reviewable IDL command plans, shows the plan, executes it
against the deterministic daemon, and narrates the structured response.
This reference implementation uses a deterministic rule-based compiler;
see openai_compiler.py for an optional model-backed drop-in.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import uuid

MODULE_ALIASES = {
    "pln": "pln",
    "ecan": "ecan_attention",
    "ecan_attention": "ecan_attention",
    "attention": "ecan_attention",
    "pattern": "pattern_matcher",
    "pattern_matcher": "pattern_matcher",
    "matcher": "pattern_matcher",
    "atomspace": "atomspace_core",
    "atomspace_core": "atomspace_core",
    "sensory": "sensory_gateway",
    "sensory_gateway": "sensory_gateway",
    "gateway": "sensory_gateway",
    "homeostat": "homeostat",
}

ENGINEER_METHODS = {"pause_module", "resume_module", "set_attention",
                    "inject_atom", "set_tc_phase", "shutdown"}


def _module_in(text: str) -> str | None:
    for token in re.findall(r"[a-z_]+", text.lower()):
        if token in MODULE_ALIASES:
            return MODULE_ALIASES[token]
    return None


def compile_intent(text: str) -> list[dict]:
    """Deterministically compile user intent into an IDL command plan."""
    t = text.lower().strip()
    mod = _module_in(t)

    m = re.search(r"set +attention +(?:of|for)? *([a-z_]+)? *to +([0-9.]+)", t)
    if m:
        target = MODULE_ALIASES.get(m.group(1) or "", mod)
        return [{"method": "set_attention",
                 "params": {"module_id": target, "value": float(m.group(2))}}]
    m = re.search(r"set +(?:tc +)?phase +(?:offset +)?(?:of|for)? *level +(\d+) +to +(-?\d+)", t)
    if m:
        return [{"method": "set_tc_phase",
                 "params": {"level": int(m.group(1)), "offset_us": int(m.group(2))}}]
    if "pause" in t and mod:
        return [{"method": "pause_module", "params": {"module_id": mod}}]
    if "resume" in t and mod:
        return [{"method": "resume_module", "params": {"module_id": mod}}]
    m = re.search(r"inject +(?:an? +)?atom +(?:named +|called +)?([a-z0-9_:-]+)", t)
    if m:
        return [{"method": "inject_atom", "params": {"name": m.group(1)}}]
    m = re.search(r"trace +(?:atom +)?([a-z0-9_>-]+)", t)
    if m:
        return [{"method": "trace_atom", "params": {"name": m.group(1)}}]
    if "shutdown" in t or "stop the daemon" in t:
        return [{"method": "shutdown", "params": {}}]
    if "hierarchy" in t or "levels" in t or "crystal" in t:
        return [{"method": "get_tc_hierarchy", "params": {}}]
    if ("why" in t or "diagnos" in t or "health" in t) and mod:
        return [{"method": "get_module", "params": {"module_id": mod}},
                {"method": "diagnose", "params": {"scope": "module", "target": mod}}]
    if "diagnos" in t or "health" in t:
        return [{"method": "diagnose", "params": {"scope": "system"}}]
    if "explain" in t or "decision" in t:
        return [{"method": "explain_decision", "params": {}}]
    if "module" in t and mod:
        return [{"method": "get_module", "params": {"module_id": mod}}]
    if "module" in t:
        return [{"method": "list_modules", "params": {}}]
    if "status" in t or "state" in t or "running" in t:
        return [{"method": "get_status", "params": {}}]
    return []


class DaemonClient:
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.rfile = self.sock.makefile("r", encoding="utf-8")

    def call(self, method: str, params: dict, access_level: str) -> dict:
        req = {"id": uuid.uuid4().hex[:8], "method": method,
               "params": params, "access_level": access_level}
        self.sock.sendall((json.dumps(req) + "\n").encode())
        return json.loads(self.rfile.readline())

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


def narrate(method: str, resp: dict) -> str:
    if not resp.get("ok"):
        err = resp.get("error", {})
        return f"  !! {err.get('code')}: {err.get('message')}"
    r = resp["result"]
    if method == "get_status":
        return (f"  Daemon running at tick {r['tick']} "
                f"({r['sim_elapsed_us'] / 1e6:.1f}s sim time); "
                f"{r['modules_total']} modules ({r['modules_paused']} paused), "
                f"total load {r['total_load']:.3f}, {r['atoms']} atoms, "
                f"{r['decisions_recorded']} decisions on record.")
    if method == "list_modules":
        rows = [f"    {m['module_id']:<16} levels={m['levels']} "
                f"attn={m['attention']:.3f} load={m['load']:.3f}"
                f"{'  [PAUSED]' if m['paused'] else ''}" for m in r["modules"]]
        return "  Modules:\n" + "\n".join(rows)
    if method == "get_module":
        return (f"  {r['module_id']}: levels {r['levels']} ({', '.join(r['level_names'])}), "
                f"attention {r['attention']:.3f}, load {r['load']:.3f}"
                f"{', PAUSED' if r['paused'] else ''}.")
    if method == "get_tc_hierarchy":
        rows = [f"    L{lv['level']:<2} {lv['name']:<24} period={lv['period_us']}us "
                f"phase={lv['phase']:.3f} modules={','.join(lv['modules']) or '-'}"
                for lv in r["levels"]]
        return "  Time crystal hierarchy:\n" + "\n".join(rows)
    if method == "diagnose":
        head = (f"  Diagnosis of {r['target']} at tick {r['tick']}: "
                f"{'HEALTHY' if r['healthy'] else 'ATTENTION NEEDED'}")
        rows = [f"    [{f['severity']}] {f['check']}: {f['detail']}"
                for f in r["findings"]] or ["    no findings"]
        return head + "\n" + "\n".join(rows)
    if method == "explain_decision":
        d = r["decision"]
        return (f"  Decision {d['decision_id']} ({d['kind']}) at tick {d['tick']}: "
                f"{d['rule']}\n    inputs={json.dumps(d['inputs'])}\n"
                f"    outputs={json.dumps(d['outputs'])}")
    if method == "trace_atom":
        a = r["atom"]
        return (f"  {a['type']} '{a['name']}' [{a['handle']}] tv={a['tv']} "
                f"out={r['outgoing'] or '-'} in={r['incoming'] or '-'}")
    return "  " + json.dumps(r)


def run_query(client: DaemonClient, text: str, access_level: str) -> bool:
    plan = compile_intent(text)
    if not plan:
        print("  (no IDL compilation for that intent; try 'status', 'list modules', "
              "'diagnose', 'show hierarchy', 'explain decision', 'trace atom <name>')")
        return True
    blocked = [c["method"] for c in plan
               if c["method"] in ENGINEER_METHODS and access_level != "engineer"]
    if blocked:
        print(f"  refusing to compile {blocked} at access level '{access_level}'; "
              "switch with /engineer")
        return True
    print("  plan: " + json.dumps(plan))
    alive = True
    for cmd in plan:
        resp = client.call(cmd["method"], cmd["params"], access_level)
        print(narrate(cmd["method"], resp))
        if cmd["method"] == "shutdown" and resp.get("ok"):
            alive = False
    return alive


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--access", choices=["technician", "engineer"],
                    default="technician")
    ap.add_argument("--once", default=None,
                    help="compile+run a single query and exit")
    args = ap.parse_args()

    try:
        client = DaemonClient(args.host, args.port)
    except OSError as exc:
        print(f"cannot reach daemon on {args.host}:{args.port}: {exc}")
        return 1

    if args.once is not None:
        print(f"> {args.once}")
        run_query(client, args.once, args.access)
        client.close()
        return 0

    level = args.access
    print("time-crystal sidecar ready. /tech /engineer /quit; natural language "
          "otherwise.")
    while True:
        try:
            text = input(f"[{level}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/engineer":
            level = "engineer"
            print("  access level: engineer")
            continue
        if text == "/tech":
            level = "technician"
            print("  access level: technician")
            continue
        if not run_query(client, text, level):
            break
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
