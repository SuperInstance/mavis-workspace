# SYN-LANE-A — the instrument that cannot report failure

**STATUS: STUB (alive). Lane started 2026-10-01T20:33Z. Filled in below as sections land.**

## The merged finding

Three lanes, one defect class. *An instrument that reports success because it cannot
report failure.*

| Instance | Symptom | Scale |
|---|---|---|
| Lane CI | workflow with no step that can exit non-zero | 23 workflows, 18 are `echo "No CI configured"` |
| Lane SPRINT-2R | test entrypoint whose exception path returns 0 | 13 repos, 11 one fail-open `try/except` in a 6-line file, 10 in `substrate-*` |
| Lane A (me) | eval split that leaks near-duplicates across the boundary | FNV-1a 64-bit scored 0.9586 > 84-column observation; honest by-ply split 0.5045 = chance |

All three are a green light wired to nothing. This lane builds ONE instrument that catches all
three, in the house style of `fleetset/fleetlint`, and calibrates it against constructed
failures BEFORE it runs on the fleet.

## Deliverables (in progress)

1. `fleetlint_canfail.py`  — `can-fail-ci` rule. PENDING
2. `fleetlint_failopen.py` — `fail-open-harness`. **EXISTS (SPRINT-2R, 4 calibration attempts). Reading + extending, not replacing.**
3. `fleetlint_pipeline.py` — `pipeline-hides-failure` (`producer | tail`). PENDING
4. `adversarial_split.py`   — group-aware + difficulty-stratified splits, naive-vs-adversarial gap. PENDING
5. `negctl/`               — negative controls: every rule fires on a constructed failure, stays quiet on a constructed success. PENDING

## Constraints honoured

- No push to GitHub. Local only; orchestrator pushes.
- No Cloudflare deploy. Name-freedom checked, not claimed.
- Every rule: 1 constructed failure it catches + 1 constructed success it does not.
- Over-firing is reported and calibrated, never quietly loosened.

---
*stub written 2026-10-01T20:33Z — sections replaced in place, do not lose this line*
