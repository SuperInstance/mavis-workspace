# DELETION EXPERIMENT — is the compulsory tissue necessary, or is it a label?

2026-10-03. **The sufficiency-by-deletion experiment, run on a real repo, with the
prediction committed before the deletion and the control arm measured before either.**

**Subject:** `SuperInstance/quilt-cell-harness` @ `b41966d8` (Python, 2680 lines, no
test files — stated in §2, it changes the design).
**Branch:** `witness/2026-10-03-deletion-witness_compartment` (local; see §7 for why it
is not on the remote).
**Reading order:** `NEURO-QUILT.md` first. The finding being tested is
Toker & Samarasinghe, *British Journal of Anaesthesia* (2026), DOI
`10.1016/j.bja.2026.07.062`: propofol on a cortical assembloid with **no thalamus**
produces the slow-wave signature; removing the inhibitory neurons abolishes it.
**Only the built absence could show that.**

---

## 0. The result in three lines

1. **Deleting the `witness_compartment` did not stop the cell witnessing.** Receipts
   still verify, 0 invalid, 64/64 seeds. **The tissue named "witness" does not
   produce the witness.**
2. **The necessity check that should have caught it is self-referential and stayed
   green.** `compulsory_missing()` computes `required − crystallized` where
   `required` *is* the declaration the deletion edited.
3. **What actually broke was a layer the probe did not cover: `qult.py` dies with
   `KeyError: 'echo'`, exit 1.** Not a red organ check. A construction-time crash.

---

## 1. The prediction, and its receipt

Committed as **`609da8a`, "PRE-REGISTRATION", 2026-10-03T17:55:29Z** — a commit that
changes no source file. The deletion is the commit after it (`7e92779`; two
housekeeping commits follow, `a5da155` and `fdcb804`, removing a stray `__pycache__` and
an empty scratch file — **no source file changes between `b41966d8` and `fdcb804` other
than `cell.py`**). Full text: `deletion-experiment/PREDICTION.md`.

**The tissue, stated without hedging:** `COMPULSORY_TISSUE["witness_compartment"] =
"echo"` — *"records receipts (uses echo to mirror)"*. The deletion removed the
**tissue**, not its label: the `COMPULSORY_TISSUE` entry, `def echo`, the
`Engine.substrates` entry, and the `__post_init__` seed compartment. 11 insertions,
6 deletions in `cell.py`; `main` untouched.

| # | predicted | outcome |
|---|---|---|
| 1 | the coverage check goes red: `n_compulsory_missing` 0 → 1, naming the missing substrate | **FALSIFIED — stayed 0.** The mechanism is §5 |
| 2 | every capability predicate true in control stays true: receipts verify, cell alive, `pto.do` callable, PTO ports live, seeded refusals fire, community still dead for the same reason | **CONFIRMED, exactly — 24 of 35 metrics bit-identical, 0 of the 9 capability predicates altered** |
| 3 | hashes, canaries, event counts **will** differ, because routing is `hash % len(substrates)` and 4 → 3 re-maps every input — a confound of the method, named in advance so it cannot be read as a finding afterwards | **CONFIRMED.** `routing.stub_llm` 4 → 7 (+75%, far outside the 30% band), `chain_len` 23 → 22, `canary` and `chain_sha` both differ |
| 4 | adaptive refusal is a **floor at 0.0 in control** and carries no information either way | held — not read, as promised |

---

## 2. The control arm, measured before anything was touched

`deletion-experiment/control.json`, **64 seeds (0–63), pinned pristine worktree**
`/workspace/repos/qch-control` at `b41966d8`, `git diff --quiet HEAD -- '*.py'` clean
at measurement time, `cell.py` sha256 `6593f7a9…`. The workload is **byte-identical in
all three arms** (same 15-energy pool, same seed sequence, same forbidden energy) — only
the tissue differs.

**The repo ships no tests.** No `test_*.py`, no `pytest.ini`, no CI config. So "the
others still work" could not be asserted from the repo's own suite — it had to be
**built and measured**, which is what `probe.py` is: 35 metrics read only through the
public surface (`process`, `is_alive`, `pto.do`, `canary`, `Quilt.ask`) and **naming no
substrate**, so it survives substrate deletion by construction.

| capability | control | spread over 64 seeds |
|---|---|---|
| witness receipts verify | **1.0** | none (64/64) |
| invalid receipts | **0** | none |
| witness chain SHA | `227f66de…` | **none — 1 distinct value in 64 seeds** |
| cell `is_alive()` | **True** | none |
| crystallised mechanism callable via `pto.do` | **True** | none |
| `pto.state` / `pto.constraints` / `pto.witness` | **True ×3** | none |
| seeded refusals fire (`DROP TABLE` ×2) | **yes** | none |
| `n_compulsory_missing` | **0** | none |
| routing count, `echo` | **3** | none |
| crystallised compartments | **4** | none |
| community `is_alive()` | **False** | none (64/64) |
| community reason | `insufficient specialisation` | none |
| **adaptive refusal** | **0.0** | none (**64/64 FAIL**) |

## 3. The noise floor — measured, not borrowed

FlyWire's own edge analysis (`Nature` `s41586-024-07686-5`) sets the fleet-wide rule:
differences of **≤30%** may be technical noise. **Here that is the wrong band, and the
control arm is why.** The cell routes by `sha256`, not by RNG, so **24 of 35 metrics
have exactly zero seed-to-seed spread.** The floor for this instrument is **0.0,
measured** — any variance would be a bug, not noise. So the test for those 24 is
**exact equality**; the 30% rule is retained only as a secondary check on the three
ratios that move, and it is reported against.

**One metric has real variance and is read accordingly:** `comm.n_edges`,
control **5.20 [4..6]**, deletion **5.375 [4..6]** — **inside the control band, not a
result.** Declared, not decided after the fact.

**Two metrics are floor effects and are not read as results at all:** community
`is_alive()` is already **False at 0.0 in the control arm** (an unbiased workload
gives all three cells the same top substrate, so condition 2 fails on 64/64 seeds;
`quilt.py --demo` only passes because it *biases* each cell to a different substrate).
And adaptive refusal is **0.0 in control**. **You cannot delete your way below zero.**

---

## 4. Specificity — one thing stops, the rest verifiably run

Arm B (tissue + requirement deleted) vs arm A, all 64 seeds, `COMPARE-deletion.txt`:

**Changed (8):** `routing.echo` 3 → 0 (substrate gone) · `cryst.n_crystallized` 4 → 3 ·
`witness.events.CRYSTALLIZED` 4 → 3 · `witness.chain_len` 23 → 22 ·
`routing.stub_llm` 4 → 7 (the predicted modulus re-map) · `chain_sha`, `state.canary`,
`quilt_canary` (different bytes, same capability).

**Exactly preserved (24 of 35, `EQUAL(exact)` against a zero-width control band),**
including every capability predicate the prediction claimed would survive:
`all_refs_valid` 1 · `n_refs_invalid` 0 · `cell_alive` True · `pto_do_ok` True ·
`pto_state/constraints/witness_ok` True ×3 · `events.REFUSED` 2 · `events.PROCESSED` 15 ·
`events.EXCEPTION` 2 · `comm.quilt_alive` False, same reason · `comm.n_distinct_roles` 1 ·
`routing.reverse` 4 · `routing.sha256` 4 · `grid_len` 15 · all six adaptive-refusal
metrics. **1 more metric** (`comm.n_edges`) moved but sits **inside** the control band.
**8 changed** (`routing.echo` is absent from the deletion arm by construction).

**Verdict: the prediction was specific, in the assembloid's sense — the named thing
stopped, everything else ran.** And that is the sharp result, because **specificity
here falsifies necessity**: the capability the tissue is named for is **unaffected by
the tissue.** `WitnessChain` is a dataclass written by `Cell.process` step 4 with
`hashlib.sha256`; not one line of it passes through the `echo` compartment. The
`witness_compartment` entry is **decorative**. `main` still runs, crystallises, and
makes cross-cell calls.

---

## 5. What stopped working that I did not predict — and it is not a capability

**5a. The necessity check cannot fail. It is satisfied by the declaration, not the cell.**

```python
def compulsory_missing(self):
    crystallized_substrates = {...}          # what the cell actually has
    required = set(COMPULSORY_TISSUE.values())  # what the cell CLAIMS to need
    return list(required - crystallized_substrates)
```

I deleted the `witness_compartment` entry. So `required` shrank to match, and
`required − crystallized` is empty again. **`n_compulsory_missing` = 0 on 64/64
seeds, with the substrate physically absent from `Engine.substrates`.** The community
check (`quilt.py:150-157`, `Quilt.is_alive` condition 5) is the same shape and behaves
the same way: its reason list is unchanged.

**In the assembloid, removing the inhibitory neurons made the criterion go red — the
criterion was independent of the thing removed. Here the criterion is the thing
removed.** A liveness predicate computed from the same declaration the mutation edits
**cannot fail that mutation.** That is the generalisable defect, and it is worth more
than the deletion.

**5b. The control arm that separates "unnecessary" from "cannot notice" — arm C.**

Arm C: **requirement restored, tissue still absent** (one line back in
`COMPULSORY_TISSUE`, `echo` still gone from the substrates). 64/64 seeds:

- `n_compulsory_missing` **0 → 1**, naming `echo`
- `quilt_reasons` gains **`missing community organs (substrates): {'echo'}`**
- …and `cell_alive` is still **True**, `quilt_alive` still **False**,
  `all_refs_valid` still **1.0**, `pto_do_ok` still **True**

So the check *can* notice, and when it does, **the witness still verifies with the
tissue officially missing.** The bookkeeping and the capability are decoupled in both
directions. This is the control the brief asked for, and it did not come from the
main experiment — it came from asking what the green result in §4 actually meant.

**5c. The hard crash — the one that surprised me most.**

```
$ python3 qult.py --demo        # control, pristine b41966d8
  quilt_beta         alive=True  cells=4  crystallized=4      <- completes

$ python3 qult.py --demo        # this branch
KeyError: 'echo'   qult.py:209  <- build_quilt("quilt_alpha", lead_substrate="echo"), line 246
exit=1
```

`qult.py` hard-codes the substrate roster in **five** places (`157, 201, 209, 229,
246`). The fractal-composition layer does not report a missing organ — **it dies at
construction.** And `qult.py:157` holds a **second, independent copy** of the
requirement set: the one place in the repo that would have caught this cleanly is
**downstream of the crash.**

**Why this is the honest headline, not a footnote:** my probe covered `cell.py` and
`quilt.py` and reported "the rest verifiably runs" — **and `qult.py` was outside the
probe.** I only found it because I ran the repo's own demos after the deletion. **A
capability census that names no substrate is still a census of the files you thought
to point it at.** The deletion was **not** specific at the module level: one layer
survived intact, one crashed.

**5d. Separate, and bigger: the control arm found a live defect, unrelated to the
deletion.** `NudgeSubstrate.grow()` forbids `sha256(str(energy))[:8]`;
`would_refuse()` tests `pattern in str(energy)`. **The grown constraint can never
match the energy that produced it.** All 64 control seeds: the cell hits an exception,
`forbidden` grows 3 → 4, the chain witnesses `exception:RuntimeError`, the refusal
counter increments — and **re-driving the same energy errors again, 64/64.** The
forbidden list carries a phantom entry (`4de8e675: 0`, matched zero times). **The
cell witnesses a refusal that never happens — a receipt with no referent**, in a repo
whose central claim is that receipts are the proof. Fix belongs in `grow()` /
`would_refuse()` and outlives this branch.

---

## 6. The doctrine, now with a measurement attached

> **To test whether a structure is necessary, build the system without it. To test
> whether it is sufficient, build the system with only it.**

Three days of this project circled the *first* half. The second half is what ran here,
and it produced a result the first half could not have:

- **A capability census is cheap only if it names no substrate.** `probe.py` reaches the
  cell only through `process` / `is_alive` / `pto.do` / `canary` / `Quilt.ask`, and
  **references no substrate identifier** — the two `echo` strings in it are three
  workload *energy* strings and one shell `echo`, not the substrate, so the same
  instrument measured both arms and the workload was held byte-identical across
  them. That is the `ASCIIPORT.md` shape — the general layer emits text, the specific
  layer is replaceable — except here the specific layer is a *requirement*.
- **The criterion must survive the thing you remove.** In the assembloid it did; here
  it was edited by the deletion. **An assay that is defined by the declaration under
  test is a tautology with extra steps.** Rank any "necessity" claim by whether its
  check reads an independent source.
- **Count the files your census points at.** 5c was a layer I never pointed the probe
  at. `grep -rn "substrates\[" --include=*.py` — 6 hits — is 20 seconds and found what
  64 seeds of probing did not.

---

## 7. Receipts, and what is NOT verified

**On the remote: the branch was NOT pushed.** `git push` fails —
`Invalid username or token. Password authentication is not supported` — the only
credential on this box is the expired `x-access-token` in `~/.gitconfig`, and `gh` is
not installed. **This is box-wide, not repo-specific**: the same failure blocks
`fleet-triage` (this report's own commit `e454368` is local-only for the same reason).
`git ls-remote origin` on `SuperInstance/quilt-cell-harness` shows **`refs/heads/main`
at `b41966d8` and nothing else**, which is the remote's actual state, read rather than
assumed. **Per `WITNESS-BRANCHES.md` step 5, the branch is therefore not claimed as
delivered.** Instead:

- `deletion-experiment/witness-deletion-witness_compartment.bundle` (333,100 bytes,
  `git bundle verify` → *"records a complete history"*, both refs present, branch head
  `fdcb804`). Pushable with a live token in one command:
  `git push <url> refs/heads/witness/2026-10-03-deletion-witness_compartment`.
  **No PR, no merge request, no issue** — and none should be opened.

**Other limits, stated:**
- `llm_cell.py` was **not measured** (needs a live LLM endpoint + key). It
  registers its own substrate (`zai_llm`) and does not reference the deleted one, so
  I expect no effect — but that is an expectation, not a measurement.
- `qult.py` is characterised **only by its crash**, not by a full census. Arm C and
  arm B are identical in `qult.py`; the crash is the whole difference.
- The probe's exception path reaches `process()`'s error branch by swapping a
  transform on an existing tiling compartment (routing is hash-determined and cannot
  be steered), so the raiser is in-place. Stated rather than hidden.
- The probe measures 35 metrics on `cell.py` and `quilt.py`. It is not a whole-repo
  proof, and §5c is the receipt for why that distinction is load-bearing.

**Artifacts** (all under `research/deletion-experiment/`, `stat -c %s` verified):
`PREDICTION.md` 4,754 · `probe.py` 11,284 · `compare.py` 3,662 · `control.json`
104,784 · `deletion.json` 104,034 · `armC.json` 108,595 · `COMPARE-deletion.txt` 6,360
(24 `EQUAL(exact)` / 9 `CHANGED` / 1 inside-band) · `COMPARE-armC.txt` 6,545 ·
`armC-qult-crash.txt` 972 · `control-qult-runs.txt` 229 ·
`witness-deletion-witness_compartment.bundle` 333,100 — mirrored in the witness branch
as `deletion-experiment/` alongside `WITNESS-2026-10-03-deletion-witness_compartment.md`.
