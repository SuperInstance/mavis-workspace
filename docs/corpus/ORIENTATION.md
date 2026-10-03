# ORIENTATION — read this first, it is cheaper than re-deriving

For any agent working in `SuperInstance`. Everything here is already established.
**Do not re-derive it. Do not report it as new. Build on it or break it.**

Files, in the order worth reading: `docs/INDEX.md` → `docs/DOCTRINE.md` →
`docs/EXPERIMENTS.md` → `docs/CORRECTION-PROJECTION.md` →
`docs/CORRECTION-CONSERVATION.md` → the lane reports in `reports/`.

---

## The one sentence everything hangs from

> **A well-formed, checkable, wrong artifact, and no instrument that can say so.**

Confirmed dozens of times in one session. Every finding below is an instance of
it. When you find something new, ask: **is this the same disease, or a different
one?** Naming a new disease wrongly is a cost; missing one is worse.

## The number that keeps appearing: **n_eff ≈ 2**

Six independent measurements, four unrelated domains, one constant:

| setting | n_eff |
|---|---|
| 9 frontier judges, 7 vendors, NLI, 100 human annotations/item | **2.18** [2.07, 2.31] |
| 16-vote panel, 330 real A/B tests | **~2** |
| 4 learners on one of our own experiments | **1.48** |
| 11 of our own reports | **2.52** (1.63 core) |
| 7 free models, across 4 different topologies | **0.165 – 0.201** |

**Consequence, and it is the single most load-bearing fact here:** a panel of
judges is worth about two votes. Adding judges, adding models, chaining them,
forking them, and varying their inputs all land in the same place. **The
correlation is in the models' priors, not in the wiring.** Do not propose a
design that scales a panel and calls the result independence.

**What does work:** buy *refinement* from a panel (it measurably improves one
framing) and buy *divergence* from different **inputs**, not different models.

## Five established facts — do not re-check, do re-use

1. **The conservation paper's theorem is stated over code that never existed.**
   `murmur/logtensor/transforms/rubiks.py`, never present in any branch. The
   fabrication is confined to the one subsystem carrying the theorem —
   `BattenSpline` (136 code hits) and the Confidence Cascade are **real**.
2. **A `6.8×` constant sits in `eisenstein` README, CONTRIBUTING, `src/lib.rs`
   and two passing property tests**, and a paper cites that suite as its
   verification. True ratio is **3.296×**. The test asserts `>= 16`, so it
   **passes at any value whatsoever.**
3. **A random split lies.** A 64-bit irreversible hash scored **0.9586** on a
   random split, above a complete 84-column observation, and **0.5045** on the
   honest by-ply split. FNV-1a has poor avalanche. **No gap smaller than the
   spread is a finding.**
4. **JEV is effectively deterministic and its panel equals one judge.** 1 of 22
   claims changed across 3 repeats, spread 0.009. One **confident false at
   p = 0.633**. `selectlib` independently measures a judge **losing to a free
   local statistic at every budget** on the condition built for it. **Do not
   build a design whose load-bearing primitive is a judge panel.**
5. **A structure with no stated invariant cannot be wrong in a noticeable way.**
   Of 988 "mathematical spreadsheet types", **48 carry an explicit invariant and
   940 do not.** That ratio is the same disease as items 1 and 2.

## Hard-won operational rules

- **Fresh clone, then run.** Not the workspace, not a summary. "Checks green" on
  a stale SHA has burned this fleet repeatedly.
- **`set -o pipefail`, or check `${PIPESTATUS[0]}`.** `producer | tail -1` hides
  producer failure and has hidden it here.
- **A control that cannot fail is worse than no control.** "I wrote a control
  that could not pass, then read its failure as a field bug" — `selectlib`, on
  its own prior conclusion.
- **A negative is a result.** "30 of 44 are empty and 4 were inspected in
  detail" beats a story about all 44. A lane once correctly refused to name a
  database it had not read, and that was the right call.
- **A failed fetch is `UNVERIFIABLE`, not false.** Keep the two apart.
- **An empty result and an inaccessible one are different findings.** Do not
  merge them.
- **Never report `p99 == p50 == mean` as a distribution.** A zero-variance
  "distribution" is a constant; check for that first.
- **Confirm a repo exists before you touch it.** Two repos were clobbered in one
  session by assuming a name was free.
- **`/tmp` is wiped in this environment.** Push anything you want to survive.
- **Env var names are exact:** `CLOUDFLARE_TOKEN`, `TYPESAFEAI_KEY`,
  `MINIMAX_KEY`, `GITHUB_TOKEN`, `OPENROUTER_KEY`. Three lanes died guessing
  `CLOUDFLARE_API_TOKEN`.

## Live surfaces

- `https://fleet-resolver.prong-potassium.workers.dev` — claim resolver, public,
  no auth, 477 repos / 85,990 files. **Backticks required; silent zero without
  them — a known bug, being fixed.** Org/repo paths unsupported.
- `https://github.com/SuperInstance/quilt-adjudication` — the competition entry.
  `bash tests/pins_quiltgit.sh` then `./demo.sh`. **No judge in the loop, by
  design, and the record it writes says so.**
- 44 D1 databases, 467 tables, 26 non-empty, **18 inaccessible and not yet
  explained.** `INACCESSIBLE` ≠ `EMPTY`.
- 69 Workers AI models free on the account; `@cf/baai/bge-m3` embeddings
  verified working and used for every n_eff measurement in this project.

## What every lane must end with

Not a summary. **This section:**

> **What I learned that changes what someone else should do.**

If a lane produces findings and no change in what the next person should build,
it has produced a receipt. Say so plainly rather than padding.

## Three things still open

1. **The CRDT layer** — 8 ports, `merge` a no-op in 3, `remove` never tombstones
   in 3, canary incapable of failing since `dcbdeca` (2026-09-30).
2. **`demotion_receipts`** in a live D1 table — a witness record for a claim
   leaving canon. **A table name is a hypothesis about behaviour, not evidence
   of it.** The write path is unverified.
3. **The algebraic/judgment ratio** of real human work. Nobody has measured it.
   If a table is 95% algorithmic, the interesting artifact is the 5%.

## If you find an error here

**Fix it and say so.** Three of these entries exist because a lane checked me
and I was wrong. `BattenSpline` has 136 code hits and I published that it was
prose-only. That correction is worth more than the error.
