# Time Crystal Daemon — IDL Specification

All interaction with the daemon flows through this typed command surface.
Transport is JSON-lines over a local socket (TCP `127.0.0.1:8377` by default;
`--socket <path>` uses AF_UNIX where the platform supports it).

## Wire format

Request (one JSON object per line):

```json
{"id": "req-1", "method": "get_status", "params": {}, "access_level": "technician"}
```

Response:

```json
{"id": "req-1", "ok": true, "result": {"state": "running", "tick": 42000}}
{"id": "req-1", "ok": false, "error": {"code": "access_denied", "message": "..."}}
```

Every command is appended to the audit log (`daemon/audit.log.jsonl`) with its
tick, parameters, access level, and outcome.

## Access levels

| Level | Commands |
|-------|----------|
| `technician` | read-only surface below |
| `engineer` | everything, including mutations |

## Technician commands (read-only)

| Method | Params | Returns |
|--------|--------|---------|
| `get_status` | — | tick, sim time, module/pause counts, total load, atom + decision counts |
| `list_modules` | — | id, levels, attention, paused, load per module |
| `get_module` | `module_id` | module detail incl. per-level phases and level names |
| `diagnose` | `scope` = `system`\|`module`, `target` | `healthy` flag + findings (severity, check, detail) |
| `trace_atom` | `handle` or `name` | atom, incoming links, outgoing set |
| `get_tc_hierarchy` | — | all 12 levels with period, live phase, offset, resident modules |
| `explain_decision` | `decision_id` (optional; latest if omitted) | deterministic decision record: kind, tick, inputs, outputs, rule |

## Engineer commands (mutations)

| Method | Params | Effect |
|--------|--------|--------|
| `pause_module` | `module_id` | freezes module; load drops to 0 |
| `resume_module` | `module_id` | reactivates module |
| `set_attention` | `module_id`, `value` ∈ [0,1] | sets STI weight; renormalized at next rebalance (every 1000 ticks) |
| `inject_atom` | `name`, `type?`, `tv?`, `out?` | adds atom to the atomspace |
| `set_tc_phase` | `level` 0–11, `offset_us` | applies phase offset to one oscillator |
| `shutdown` | — | stops the daemon after replying |

## Error codes

`unknown_method`, `access_denied`, `bad_access_level`, `bad_params`,
`no_such_module`, `no_such_atom`, `no_decisions`, `no_such_decision`,
`bad_request`.

## Determinism contract

State evolution is a pure function of the tick counter: phases derive from
`(tick × 1000µs + offset) mod period`, attention rebalances on fixed tick
boundaries, and every mutation is recorded as a decision. `--selftest` runs
the same scripted simulation twice and compares SHA-256 state digests plus
command outputs, and verifies access gating.

## Modules and their TC levels

| Module | Levels | Role |
|--------|--------|------|
| `sensory_gateway` | 1–3 | ion-channel/membrane-scale input |
| `atomspace_core` | 4–6 | hypergraph store |
| `pattern_matcher` | 5–7 | subgraph matching |
| `pln` | 6–8 | probabilistic logic inference |
| `ecan_attention` | 7–9 | attention economy |
| `homeostat` | 10–11 | circadian/homeostatic regulation |
