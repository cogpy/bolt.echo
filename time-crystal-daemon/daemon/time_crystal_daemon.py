#!/usr/bin/env python3
"""Time Crystal Daemon — deterministic cognitive kernel.

Sidecar pattern core: a long-running, fully deterministic process organized
around a 12-level hierarchical temporal oscillator (Nanobrain Fig 7.15).
All interaction happens through a typed IDL over a JSON-lines socket.
The daemon never consults an LLM: state evolution depends only on the tick
counter, so any run is exactly reproducible (see --selftest).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import socket
import socketserver
import sys
import threading
import time

# ---------------------------------------------------------------------------
# Time crystal hierarchy (level, name, period in microseconds, domain)
# ---------------------------------------------------------------------------

TC_LEVELS = [
    (0, "quantum_resonance", 1, "Quantum effects"),
    (1, "protein_dynamics", 8_000, "Protein channels"),
    (2, "ion_channel_gating", 26_000, "Ion channels"),
    (3, "membrane_dynamics", 52_000, "Membrane"),
    (4, "axon_initial_segment", 110_000, "AIS"),
    (5, "dendritic_integration", 160_000, "Dendrites"),
    (6, "synaptic_plasticity", 250_000, "Synapses"),
    (7, "soma_processing", 330_000, "Soma"),
    (8, "network_synchronization", 500_000, "Network"),
    (9, "global_rhythm", 1_000_000, "Global"),
    (10, "circadian_modulation", 60_000_000, "Circadian"),
    (11, "homeostatic_regulation", 3_600_000_000, "Homeostatic"),
]

TICK_US = 1_000  # one tick advances simulated time by 1 ms

# Cognitive modules and the TC levels they oscillate on.
MODULES = {
    "sensory_gateway": {"levels": [1, 2, 3], "attention": 0.10},
    "atomspace_core": {"levels": [4, 5, 6], "attention": 0.20},
    "pattern_matcher": {"levels": [5, 6, 7], "attention": 0.15},
    "pln": {"levels": [6, 7, 8], "attention": 0.25},
    "ecan_attention": {"levels": [7, 8, 9], "attention": 0.20},
    "homeostat": {"levels": [10, 11], "attention": 0.10},
}

SEED_ATOMS = [
    {"handle": "a1", "type": "ConceptNode", "name": "time_crystal", "tv": [0.95, 0.90]},
    {"handle": "a2", "type": "ConceptNode", "name": "oscillator", "tv": [0.90, 0.85]},
    {"handle": "a3", "type": "ConceptNode", "name": "cognition", "tv": [0.80, 0.70]},
    {"handle": "l1", "type": "InheritanceLink", "name": "time_crystal->oscillator",
     "out": ["a1", "a2"], "tv": [0.92, 0.88]},
    {"handle": "l2", "type": "EvaluationLink", "name": "drives(oscillator,cognition)",
     "out": ["a2", "a3"], "tv": [0.75, 0.60]},
]

TECHNICIAN_METHODS = {
    "get_status", "list_modules", "get_module", "diagnose",
    "trace_atom", "get_tc_hierarchy", "explain_decision",
}
ENGINEER_METHODS = {
    "pause_module", "resume_module", "set_attention",
    "inject_atom", "set_tc_phase", "shutdown",
}
ALL_METHODS = TECHNICIAN_METHODS | ENGINEER_METHODS

REBALANCE_EVERY = 1_000  # ticks between attention-rebalance decisions


class IDLError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def q(x: float) -> float:
    """Quantize floats so digests are platform-stable."""
    return round(x, 9)


class TimeCrystal:
    """Deterministic cognitive kernel state. Evolution depends only on ticks."""

    def __init__(self) -> None:
        self.tick = 0
        self.phase_offset_us = {lvl: 0 for lvl, _, _, _ in TC_LEVELS}
        self.modules = {
            mid: {
                "id": mid,
                "levels": list(spec["levels"]),
                "attention": spec["attention"],
                "paused": False,
                "load": 0.0,
            }
            for mid, spec in MODULES.items()
        }
        self.atoms = {a["handle"]: dict(a) for a in SEED_ATOMS}
        self.decisions: list[dict] = []
        self._decision_seq = 0
        self.lock = threading.RLock()
        self._record_decision(
            "bootstrap",
            {"modules": sorted(self.modules)},
            {"attention": {m: q(s["attention"]) for m, s in self.modules.items()}},
            "initial attention allocation from static module table",
        )

    # -- deterministic dynamics ------------------------------------------------

    def elapsed_us(self) -> int:
        return self.tick * TICK_US

    def phase(self, level: int) -> float:
        period = TC_LEVELS[level][2]
        pos = (self.elapsed_us() + self.phase_offset_us[level]) % period
        return q(pos / period)

    def _module_load(self, mod: dict) -> float:
        if mod["paused"]:
            return 0.0
        acc = 0.0
        for lvl in mod["levels"]:
            ph = self.phase(lvl)
            acc += math.sin(math.pi * ph) ** 2
        return q(mod["attention"] * (0.25 + 0.75 * acc / len(mod["levels"])))

    def advance(self, n: int) -> None:
        with self.lock:
            for _ in range(n):
                self.tick += 1
                if self.tick % REBALANCE_EVERY == 0:
                    self._rebalance()
            for mod in self.modules.values():
                mod["load"] = self._module_load(mod)

    def _rebalance(self) -> None:
        active = [m for m in self.modules.values() if not m["paused"]]
        total = sum(m["attention"] for m in active)
        before = {m["id"]: q(m["attention"]) for m in active}
        if total > 0:
            for m in active:
                m["attention"] = q(m["attention"] / total)
        self._record_decision(
            "attention_rebalance",
            {"tick": self.tick, "before": before},
            {"after": {m["id"]: q(m["attention"]) for m in active}},
            "normalize attention over non-paused modules (ECAN invariant: sum==1)",
        )

    def _record_decision(self, kind: str, inputs: dict, outputs: dict, rule: str) -> None:
        self._decision_seq += 1
        self.decisions.append({
            "decision_id": f"d{self._decision_seq}",
            "tick": self.tick,
            "kind": kind,
            "inputs": inputs,
            "outputs": outputs,
            "rule": rule,
        })
        if len(self.decisions) > 256:
            self.decisions = self.decisions[-256:]

    def digest(self) -> str:
        with self.lock:
            state = {
                "tick": self.tick,
                "offsets": self.phase_offset_us,
                "modules": {k: {kk: v[kk] for kk in ("levels", "attention", "paused", "load")}
                            for k, v in sorted(self.modules.items())},
                "atoms": dict(sorted(self.atoms.items())),
                "decisions": self.decisions,
            }
        blob = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(blob).hexdigest()

    # -- IDL command surface ---------------------------------------------------

    def execute(self, method: str, params: dict, access_level: str) -> dict:
        if method not in ALL_METHODS:
            raise IDLError("unknown_method", f"unknown method '{method}'")
        if method in ENGINEER_METHODS and access_level != "engineer":
            raise IDLError("access_denied",
                           f"'{method}' requires engineer access; current level is "
                           f"'{access_level}'")
        with self.lock:
            return getattr(self, f"_cmd_{method}")(params or {})

    def _need_module(self, params: dict) -> dict:
        mid = params.get("module_id")
        if mid not in self.modules:
            raise IDLError("no_such_module",
                           f"module '{mid}' not found; known: {sorted(self.modules)}")
        return self.modules[mid]

    def _cmd_get_status(self, _p: dict) -> dict:
        active = [m for m in self.modules.values() if not m["paused"]]
        return {
            "state": "running",
            "tick": self.tick,
            "sim_elapsed_us": self.elapsed_us(),
            "modules_total": len(self.modules),
            "modules_paused": len(self.modules) - len(active),
            "total_load": q(sum(m["load"] for m in active)),
            "decisions_recorded": len(self.decisions),
            "atoms": len(self.atoms),
        }

    def _cmd_list_modules(self, _p: dict) -> dict:
        return {"modules": [
            {"module_id": m["id"], "levels": m["levels"],
             "attention": q(m["attention"]), "paused": m["paused"], "load": m["load"]}
            for m in (self.modules[k] for k in sorted(self.modules))
        ]}

    def _cmd_get_module(self, p: dict) -> dict:
        m = self._need_module(p)
        return {
            "module_id": m["id"], "levels": m["levels"],
            "level_names": [TC_LEVELS[l][1] for l in m["levels"]],
            "phases": {str(l): self.phase(l) for l in m["levels"]},
            "attention": q(m["attention"]), "paused": m["paused"], "load": m["load"],
        }

    def _cmd_get_tc_hierarchy(self, _p: dict) -> dict:
        return {"tick_us": TICK_US, "levels": [
            {"level": lvl, "name": name, "period_us": period, "domain": domain,
             "phase": self.phase(lvl), "phase_offset_us": self.phase_offset_us[lvl],
             "modules": sorted(m["id"] for m in self.modules.values()
                               if lvl in m["levels"])}
            for lvl, name, period, domain in TC_LEVELS
        ]}

    def _cmd_diagnose(self, p: dict) -> dict:
        scope = p.get("scope", "system")
        findings = []
        if scope == "module":
            m = self._need_module({"module_id": p.get("target")})
            if m["paused"]:
                findings.append({"severity": "warning", "check": "paused",
                                 "detail": f"{m['id']} is paused; load forced to 0"})
            if m["attention"] < 0.05:
                findings.append({"severity": "warning", "check": "attention_starvation",
                                 "detail": f"attention {q(m['attention'])} < 0.05"})
            if m["attention"] > 0.5:
                findings.append({"severity": "info", "check": "attention_dominance",
                                 "detail": f"{m['id']} holds {q(m['attention'])} of total "
                                           "attention; consider set_attention to rebalance"})
            target = m["id"]
        elif scope == "system":
            active = [m for m in self.modules.values() if not m["paused"]]
            att = sum(m["attention"] for m in active)
            if abs(att - 1.0) > 1e-6 and self.tick >= REBALANCE_EVERY:
                findings.append({"severity": "warning", "check": "attention_sum",
                                 "detail": f"sum(attention)={q(att)} != 1.0 "
                                           "(rebalances every 1000 ticks)"})
            for lvl, name, period, _ in TC_LEVELS:
                if self.phase_offset_us[lvl] % period != 0 and self.phase_offset_us[lvl] != 0:
                    findings.append({"severity": "info", "check": "phase_offset",
                                     "detail": f"level {lvl} ({name}) offset "
                                               f"{self.phase_offset_us[lvl]}us"})
            paused = sorted(m["id"] for m in self.modules.values() if m["paused"])
            if paused:
                findings.append({"severity": "warning", "check": "paused_modules",
                                 "detail": f"paused: {paused}"})
            target = "system"
        else:
            raise IDLError("bad_params", "scope must be 'system' or 'module'")
        return {"scope": scope, "target": target, "tick": self.tick,
                "healthy": not any(f["severity"] == "warning" for f in findings),
                "findings": findings}

    def _cmd_trace_atom(self, p: dict) -> dict:
        key = p.get("handle") or p.get("name")
        atom = self.atoms.get(key)
        if atom is None:
            atom = next((a for a in self.atoms.values() if a["name"] == key), None)
        if atom is None:
            raise IDLError("no_such_atom", f"atom '{key}' not found")
        incoming = [a["handle"] for a in self.atoms.values()
                    if atom["handle"] in a.get("out", [])]
        return {"atom": atom, "incoming": sorted(incoming),
                "outgoing": atom.get("out", [])}

    def _cmd_explain_decision(self, p: dict) -> dict:
        if not self.decisions:
            raise IDLError("no_decisions", "no decisions recorded yet")
        did = p.get("decision_id")
        if did is None:
            return {"decision": self.decisions[-1]}
        for d in self.decisions:
            if d["decision_id"] == did:
                return {"decision": d}
        raise IDLError("no_such_decision", f"decision '{did}' not found")

    def _cmd_pause_module(self, p: dict) -> dict:
        m = self._need_module(p)
        m["paused"] = True
        m["load"] = 0.0
        self._record_decision("pause", {"module_id": m["id"]}, {"paused": True},
                              "engineer-issued pause_module")
        return {"module_id": m["id"], "paused": True}

    def _cmd_resume_module(self, p: dict) -> dict:
        m = self._need_module(p)
        m["paused"] = False
        m["load"] = self._module_load(m)
        self._record_decision("resume", {"module_id": m["id"]}, {"paused": False},
                              "engineer-issued resume_module")
        return {"module_id": m["id"], "paused": False}

    def _cmd_set_attention(self, p: dict) -> dict:
        m = self._need_module(p)
        try:
            value = float(p["value"])
        except (KeyError, TypeError, ValueError):
            raise IDLError("bad_params", "set_attention requires numeric 'value'")
        if not 0.0 <= value <= 1.0:
            raise IDLError("bad_params", "value must be within [0,1]")
        before = m["attention"]
        m["attention"] = q(value)
        m["load"] = self._module_load(m)
        self._record_decision("set_attention", {"module_id": m["id"], "before": q(before)},
                              {"after": m["attention"]}, "engineer-issued set_attention")
        return {"module_id": m["id"], "attention": m["attention"]}

    def _cmd_inject_atom(self, p: dict) -> dict:
        name = p.get("name")
        if not name or not isinstance(name, str):
            raise IDLError("bad_params", "inject_atom requires string 'name'")
        atype = p.get("type", "ConceptNode")
        tv = p.get("tv", [1.0, 1.0])
        handle = f"a{sum(1 for _ in self.atoms) + 1}x"
        atom = {"handle": handle, "type": atype, "name": name,
                "tv": [q(float(tv[0])), q(float(tv[1]))]}
        if p.get("out"):
            atom["out"] = list(p["out"])
        self.atoms[handle] = atom
        self._record_decision("inject_atom", {"name": name, "type": atype},
                              {"handle": handle}, "engineer-issued inject_atom")
        return {"atom": atom}

    def _cmd_set_tc_phase(self, p: dict) -> dict:
        try:
            level = int(p["level"])
            offset = int(p["offset_us"])
        except (KeyError, TypeError, ValueError):
            raise IDLError("bad_params",
                           "set_tc_phase requires integer 'level' and 'offset_us'")
        if not 0 <= level < len(TC_LEVELS):
            raise IDLError("bad_params", f"level must be 0..{len(TC_LEVELS) - 1}")
        self.phase_offset_us[level] = offset
        self._record_decision("set_tc_phase", {"level": level}, {"offset_us": offset},
                              "engineer-issued set_tc_phase")
        return {"level": level, "name": TC_LEVELS[level][1],
                "offset_us": offset, "phase": self.phase(level)}

    def _cmd_shutdown(self, _p: dict) -> dict:
        return {"shutting_down": True}


# ---------------------------------------------------------------------------
# JSON-lines server
# ---------------------------------------------------------------------------

class DaemonServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, addr, crystal: TimeCrystal, audit_path: str):
        super().__init__(addr, Handler)
        self.crystal = crystal
        self.audit_path = audit_path
        self.audit_lock = threading.Lock()

    def audit(self, entry: dict) -> None:
        entry["wall_time"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with self.audit_lock:
            with open(self.audit_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        server: DaemonServer = self.server  # type: ignore[assignment]
        for raw in self.rfile:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            rid, response, stop = None, None, False
            try:
                req = json.loads(line)
                rid = req.get("id")
                method = req.get("method", "")
                params = req.get("params") or {}
                level = req.get("access_level", "technician")
                if level not in ("technician", "engineer"):
                    raise IDLError("bad_access_level",
                                   "access_level must be technician|engineer")
                result = server.crystal.execute(method, params, level)
                response = {"id": rid, "ok": True, "result": result}
                server.audit({"id": rid, "method": method, "params": params,
                              "access_level": level, "ok": True,
                              "tick": server.crystal.tick})
                stop = method == "shutdown"
            except IDLError as exc:
                response = {"id": rid, "ok": False,
                            "error": {"code": exc.code, "message": str(exc)}}
                server.audit({"id": rid, "ok": False, "error": exc.code,
                              "tick": server.crystal.tick})
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                response = {"id": rid, "ok": False,
                            "error": {"code": "bad_request", "message": str(exc)}}
            self.wfile.write((json.dumps(response) + "\n").encode())
            self.wfile.flush()
            if stop:
                threading.Thread(target=server.shutdown, daemon=True).start()
                return


def run_server(host: str, port: int, audit_path: str, hz: int) -> None:
    crystal = TimeCrystal()
    server = DaemonServer((host, port), crystal, audit_path)

    def ticker() -> None:
        batch = max(1, 1000 // hz)  # keep ~1000 sim-ticks/sec regardless of hz
        while True:
            time.sleep(1.0 / hz)
            crystal.advance(batch)

    threading.Thread(target=ticker, daemon=True).start()
    print(f"time-crystal-daemon ready on {host}:{port} "
          f"(audit={audit_path}, pid={os.getpid()})", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
        print("time-crystal-daemon stopped", flush=True)


# ---------------------------------------------------------------------------
# Determinism self-test
# ---------------------------------------------------------------------------

SELFTEST_SCRIPT = [
    (500, "set_attention", {"module_id": "pln", "value": 0.4}, "engineer"),
    (1200, "pause_module", {"module_id": "sensory_gateway"}, "engineer"),
    (2000, "inject_atom", {"name": "selftest_atom", "tv": [0.5, 0.5]}, "engineer"),
    (2600, "set_tc_phase", {"level": 9, "offset_us": 250_000}, "engineer"),
    (3300, "resume_module", {"module_id": "sensory_gateway"}, "engineer"),
]


def _sim_run(ticks: int) -> tuple[str, list]:
    crystal = TimeCrystal()
    outputs = []
    script = sorted(SELFTEST_SCRIPT)
    idx = 0
    step = 100
    for _ in range(ticks // step):
        crystal.advance(step)
        while idx < len(script) and script[idx][0] <= crystal.tick:
            _, method, params, level = script[idx]
            outputs.append(crystal.execute(method, params, level))
            idx += 1
    outputs.append(crystal.execute("get_status", {}, "technician"))
    outputs.append(crystal.execute("diagnose", {"scope": "system"}, "technician"))
    return crystal.digest(), outputs


def selftest() -> int:
    ticks = 5000
    d1, o1 = _sim_run(ticks)
    d2, o2 = _sim_run(ticks)
    same = d1 == d2 and o1 == o2
    try:
        TimeCrystal().execute("pause_module", {"module_id": "pln"}, "technician")
        gate_ok = False
    except IDLError as exc:
        gate_ok = exc.code == "access_denied"
    print(f"digest run A : {d1}")
    print(f"digest run B : {d2}")
    print(f"deterministic: {'PASS' if same else 'FAIL'}")
    print(f"access gating: {'PASS' if gate_ok else 'FAIL'}")
    return 0 if (same and gate_ok) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--socket", default=None,
                    help="unix socket path (falls back to TCP on Windows)")
    ap.add_argument("--audit", default=os.path.join(os.path.dirname(__file__),
                                                    "audit.log.jsonl"))
    ap.add_argument("--hz", type=int, default=50, help="ticker frequency")
    ap.add_argument("--selftest", action="store_true",
                    help="verify determinism and access gating, then exit")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.socket and not hasattr(socket, "AF_UNIX"):
        print(f"AF_UNIX unavailable on this platform; using TCP "
              f"{args.host}:{args.port}", flush=True)
    run_server(args.host, args.port, args.audit, args.hz)
    return 0


if __name__ == "__main__":
    sys.exit(main())
