# Time Crystal Daemon

A working realization of the `time-crystal-daemon` skill: a **deterministic
cognitive kernel** organized around a 12-level hierarchical temporal
oscillator, fronted by an **LLM sidecar** that compiles natural language into
typed IDL commands. The LLM is a compiler, not an oracle — the daemon never
delegates a decision to it.

```
user ──NL──▶ llm_interface/llm_sidecar.py ──IDL/JSON-lines──▶ daemon/time_crystal_daemon.py
                 (compiler + narrator)                          (deterministic core + audit log)
```

## Run

```powershell
# 1. verify determinism + access gating
python daemon\time_crystal_daemon.py --selftest

# 2. start the daemon (or scripts\run_daemon.ps1)
python daemon\time_crystal_daemon.py --port 8377

# 3. talk to it
python llm_interface\llm_sidecar.py
> What's the status?
> List all modules
> Run diagnostics
> Show time crystal hierarchy
> Why is PLN using so much attention?
/engineer
> Set attention of pln to 0.4
> Pause the sensory module
```

One-shot mode: `python llm_interface\llm_sidecar.py --once "run diagnostics"`.
Engineer one-shots: add `--access engineer`.

## Layout

| Path | Purpose |
|------|---------|
| `daemon/time_crystal_daemon.py` | deterministic core, TC hierarchy, IDL server, audit log, `--selftest` |
| `llm_interface/llm_sidecar.py` | rule-based intent→IDL compiler, plan display, narration, REPL |
| `llm_interface/openai_compiler.py` | optional model-backed compiler with strict plan validation (opt-in) |
| `references/idl_specification.md` | full typed command surface |
| `scripts/run_daemon.ps1` / `.sh` | convenience launchers |

## Design principles (from the skill)

1. **Deterministic core** — state is a pure function of the tick counter.
2. **Typed interface** — every command validated; unknown params rejected.
3. **Fail-safe** — the sidecar can die without touching daemon state.
4. **Auditable** — every command lands in `daemon/audit.log.jsonl`; every
   mutation is a recorded *decision* retrievable via `explain_decision`.
5. **Hierarchical time** — six cognitive modules ride levels 1–11 of the
   Nanobrain hierarchy (µs quantum resonance → 1 h homeostatic regulation).
