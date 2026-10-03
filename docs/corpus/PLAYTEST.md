# PLAYTEST — the mutation test, run against the fleet

**Lane:** playtester. **Date:** 2026-10-01. **Method:** get the suite green, mutate the line
the README leads with, re-run, and report the number. For every repo: flagship mutation,
control mutation, both numbers or neither.

**Nothing was fixed.** Every file mutated was restored; `git status` clean in all five
checkouts at time of writing. No commits, no pushes.

## Environment notes that change how to read the numbers

- `git commit` in a test fixture fails with `gpg failed to sign the data` until
  `git config --global commit.gpgsign false` is set. Two of pong-quilt's 301 tests
  (`conflict-marker-glue.test.js:83,97`) die on this alone and it has nothing to do with
  the code. **A first baseline of "2 red" here is an environment artifact, not a finding.**
  I set the config and re-baselined rather than reporting a red I had caused.
- `fleet-kit` has 7 pytest-only test files. Under `python3 -m unittest`, a pytest-style
  `class TestFoo:` (no `unittest.TestCase` base) is **silently collected as zero tests and
  the run still prints `OK`**. My first fleet-kit run reported "51 passed" and I had in
  fact excluded 10 `test_consensus` tests without noticing. Anything that reports a green
  count without naming its runner should be re-checked against the runner's collection
  rules.

---

## Summary

| repo | baseline | flagship mutation | control mutation | verdict |
|---|---|---|---|---|
| `pong-quilt` | 293/293 + 8/8 green | **CAUGHT** (2 red) ×4 mutations | **CAUGHT** (2 red) | **COVERS THE PRODUCT** |
| `quilt-gpu-lab` | **RED at HEAD** (1 of 6) | n/a — see below | **CAUGHT** | **ALREADY-RED** |
| `voxelglyph` | 7/7 green | **SURVIVED** ×2 | **CAUGHT** | **VACUOUS** (product), sound (arithmetic) |
| `fleetset` | — | — | — | **COULD-NOT-RUN: repo not found** |
| `fleet-kit` | 51/51 green (6 of 12 files) | **CAUGHT** (5 red) | **CAUGHT** (4 red) | **COVERS THE PRODUCT** (runnable subset) |
| `quilt-tools` | 94/94 green | **SURVIVED** | 1 of 3 **CAUGHT** | **VACUOUS** (harness + ledger-seal) |

**Two of six repos are vacuous by the flagship test, and the two vacuous ones fail in
different ways.** `voxelglyph` never executes its product. `quilt-tools` executes its
product but grades it with a `check()` that cannot fail.

---

## 1. `pong-quilt` — COVERS THE PRODUCT

This is the fleet's most-exercised suite and the place a vacuous result would be most
embarrassing. It is not vacuous. Five independent mutations, all caught.

**Baseline.** `node tools/build-site.mjs && node --test tests/*.test.js` →
**293 pass, 0 fail, 8 skipped**, 27.0 s. Plus `node --test tools/test-qa.js` → **8/8**.
(64 test files, 301 tests. The "291" in the brief is the pass count before the GPG fix.)

**Instrumentation first.** I counted executions of the flagship line before trusting any
mutation result. The README leads with *"A tiny neural net (6→10→3, tanh) plays Pong as a
genetic algorithm… the training is real computation in your browser."* The line carrying
that claim:

```
core.js:59        h.push(Math.tanh(s));
```

Instrumented with a filesystem append and re-ran the full suite:
**140,799,110 executions.** Not zero. This is the exact opposite of `logtensor`, where
instrumenting the flagship line yielded 0 occurrences.

| # | mutation | `path:line` | result |
|---|---|---|---|
| flagship | `Math.tanh(s)` → `Math.tanh(s) * 0.0` | `core.js:59` | **2 red** — `R54: gen-121 champion benches near the artifact regime`, `R57: mid-generation file-load resets the streaming evaluator` |
| control | `fitnessOf` → `frames + hits * HIT_WEIGHT * 0.0` | `core.js:78` | **2 red** — `fitnessOf: a capped 0-hit survivor…`, `checkpoints are internally consistent with the CURRENT fitness formula` |
| flagship 2 | GA mutation operator → `* sigma * 0.0` (evolution frozen) | `core.js:69` | **2 red** — `C1 breeds from the FULL scored population`, `the σ-slider is ALIVE` |
| flagship 3 | speed ramp → `frames * D.ramp * 0.0` (difficulty never escalates) | `core.js:118` | **4 red** — incl. `accel is real: speedMul follows min((1+frames*ramp)…)` |
| flagship 4 | C1 survivor net deaf → `const os = [0,0,0]` | `core.js:377` | **1 red** — `R54: gen-121 champion benches near the artifact regime` |

**Method note.** `site-glue.test.js:26-31` pins `core.js` byte-identical against
`site/dist/demo/core.js`. Mutating `core.js` alone trips that pin for the wrong reason — it
detects a *copy-fidelity* break, not a *behaviour* break. I re-ran `tools/build-site.mjs`
after every mutation so the byte-pins re-seal to the mutated tree and only behavioural
failures can go red. Without that step this repo scores a false positive.

**Verdict: COVERS THE PRODUCT.** The flagship mutation is caught by tests that re-run
actual evolution and benchmark the resulting champion, not by tests that assert
construction. This is the fleet's reference implementation for what the rest of the fleet
should be measuring against.

---

## 2. `quilt-gpu-lab` — ALREADY-RED, and the guard has an unaudited escape hatch

**Baseline: RED on a clean clone of `main` (`fb9a723`), before any mutation.**

```
FAIL: test_manifest_matches_working_tree
AssertionError: '8277d903053541f8002062683d2bf91765abaa25406959560601babb844a78b8'
              != '4a0af1f39927ac54658a969db40fab1736e4f488959a9de685ab2149bbc42d02'
: RESULTS.md drifted from the sealed digest
Ran 6 tests — FAILED (failures=1)
```

**What happened.** I bisected the pinned digest across 25 commits. `8277d903…` matches a
**legitimately committed** state of `RESULTS.md` — every commit from `2d4009b` through
`ecc8288`. This is *not* a repeat of the d23b phantom seal. The ledger simply moved twice
without a re-seal: `fc2aa79` (books PX2/PX3/PX5) and `fb9a723` (books PX6) both touch
`RESULTS.md`, and the last re-seal is `ef726a3`, whose commit message ends **"tests
green"**. That claim is false at HEAD.

**The pin is right and nothing runs it.** There is no `.github/` directory in this repo at
all — no CI workflow of any kind. The receipt layer is correct, catches the drift on the
first run, and then has no mechanism to be run again.

### 2a. The seal does not describe the tree it was cut from

`tools/receipt_manifest.py:69-88` (`build()`) emits exactly six keys: `schema`,
`generated_at`, `doctrine`, `ledgers`, `experiments`, `tools`. **No commit, no tree, no
branch, no parent.** The manifest is content-addressed only.

Measured: I created `rebase-sim`, squashed the last three commits into one (tree identical,
commit `fb9a723` → `428c69c`), and re-sealed. The only fields that changed were the content
digests and the timestamp. **No field anywhere names the new commit.** A rebase, a squash,
a re-parent — all structurally invisible to the seal, by construction. The seal can answer
"do these bytes still match?" and can never answer "which tree was this cut from?".

### 2b. The guard's own escape hatch is unaudited

`tools/receipt_manifest.py:47-64` (`dirty_sealed_paths()`) exists specifically to stop the
d23b failure class: it refuses to seal when sealed paths are dirty, and offers
`--allow-dirty`, which records a `sealed_from_dirty_tree` admission row. The d23b autopsy
receipt (`receipts/manifest-repair-2026-09-30-d23b.md`) names this as the follow-up.

I reproduced the d23b class through the sanctioned escape hatch:

1. Append an in-flight edit to `RESULTS.md`, uncommitted.
2. `python tools/receipt_manifest.py --allow-dirty` → seals the **dirty** bytes; the
   manifest now openly carries `sealed_from_dirty_tree: {admission: true, paths: [' M RESULTS.md']}`.
3. Commit that same edit.
4. Working tree now equals the sealed bytes.

```
Ran 6 tests in 0.153s
OK
```

**6/6 green, with the dirty-tree admission sitting in the manifest.** `test_receipts.py:88-107`
compares only `ledgers`, `experiments`, `tools`. It never reads `sealed_from_dirty_tree`.
The guard fires once, at seal time, and nothing audits the record it leaves behind — so the
one class the guard was invented to eliminate is still reachable, and now arrives with a
certificate saying it was allowed.

**Control.** Plain content drift with no re-seal → pin goes **RED** as it should. Method is
not inverted.

**Verdict: ALREADY-RED**, with two independent structural findings: the manifest binds no
git identity, and the dirty-seal admission is unaudited. The good news is that the pin
itself works; the failure is that nothing runs it.

---

## 3. `voxelglyph` — VACUOUS for the product, genuinely sound for the arithmetic

I merged this repo's 7-pin verification, so I tried hardest to make the pins lie. Two of
the three ways I tried worked, and the third is the one that matters.

**Baseline.** `python3 -m unittest tests.test_exp1_verification -v` → **7/7 green**, 0.27 s.

**The product is never executed.** The suite imports exactly one thing from the codebase:

```python
from syzygy_port import luma8  # instrument under test (pin 2 cross-checks it)
```

`exp1_luma_collision.py` — the experiment the entire repository is about, the file the
README's headline finding comes from — is **never imported and never run**. I registered an
`atexit` counter on it and ran the full suite: **0 executions.**

| # | mutation | `path:line` | result |
|---|---|---|---|
| flagship | `widest = max(buckets, …)` → `min(…)` — the product reports the *narrowest* class as the widest blind spot | `exp1_luma_collision.py:43` | **SURVIVED — 7/7 green** |
| flagship 2 | `STEP = 5` (52³ = 140,608 triples) → `STEP = 200` (2³ = **8** triples) | `exp1_luma_collision.py:29` | **SURVIVED — 7/7 green** |
| control | `syzygy_port.luma8` → off-by-one `+ 1` | `syzygy_port.py:26` | **CAUGHT** — `test_formula_recode_crosschecks_port` |

The control is caught, so the method is not inverted. The re-coded BT.601 luma is doing
**real** re-derivation over 140,608 lattice points and cross-checking the port properly.
The pins are not quote-machines. What they verify is a **re-implementation**, not the
product: the suite can re-derive "luma 140 is the widest class" while the product
separately reports the narrowest, and both are green.

### Two of the seven pins are literal tautologies

```python
# tests/test_exp1_verification.py:64
self.assertEqual(77 + 150 + 29, 256)      # asserts arithmetic on its own literals

# tests/test_exp1_verification.py:80
self.assertAlmostEqual(1 / 8, 0.125)      # likewise
self.assertIn("0.125", FINDINGS)          # a string grep
```

Neither ever reads `syzygy_port.py`. Proof: I set the port's real weights
`LUMA_WR = (77, 150, 29)` → `(200, 3, 91)`, summing to 294, and `test_weights_sum_256`
— whose entire purpose is to certify that the weights sum to 256 — **passed**.

**Verdict: VACUOUS for the product.** The verification layer is real arithmetic and worth
keeping; it just verifies a copy. A pin that re-derives a claim from a second implementation
is only a verification of the product if something also pins the two implementations
together.

---

## 4. `fleetset` — COULD-NOT-RUN

```
$ git ls-remote https://github.com/SuperInstance/fleetset.git
fatal: could not read Username for 'https://github.com': No such device or address
```

`fleet-kit` (`5ad1e810`) resolves; `fleetset` does not — private or renamed. Not
attempted further. No linter was playtested under that name.

---

## 5. `fleet-kit` — COVERS THE PRODUCT (for the 51 tests that actually run)

**Baseline.** 51 tests green across the 6 `unittest`-native files, 0.05 s. The other 7 of
12 files are pytest-only: **COULD-NOT-RUN: no pytest, no PyPI access** (`test_badges`,
`test_consensus`, `test_indexer`, `test_models`, `test_plugins`, `test_services`,
`test_utils` — 70 tests). Any fleet count that says "fleet-kit passes" is counting 51.

**The flagship and control both land:**

| # | mutation | `path:line` | result |
|---|---|---|---|
| flagship | heartbeat reports `load * 0.0` — every liveness ping claims the agent is idle | `fleet_kit/keeper.py:106` | **CAUGHT — 5 red** |
| control | `register` discards the capabilities it was handed | `fleet_kit/keeper.py:73` | **CAUGHT — 4 red** |

### 39 tests cannot run outside one laptop

`tests/test_audits.py:11`, `test_crab.py:10`, `test_matrix.py:11`, `test_plato.py:12` all
begin:

```python
example_dir = "/home/ubuntu/.openclaw/workspace/repos/fleet-kit"
```

In a clean clone these die at **import time** with `FileNotFoundError` before a single test
runs — 39 tests that are green only on the author's machine. I neutralised the one line in
each and got 9/9, 12/12, 8/8, 10/10. Five product modules carry the same path as a *default
argument* (`audits.py:106`, `badges.py:55`, `indexer.py:49`, `plugins.py:15`, `cli.py:176`),
so a user who omits the flag gets the author's home directory.

### The linter: no tests, cannot run, not even shipped

The orchestrator's question — does `fleetlint` over-fire? — **cannot be answered here, and
that is itself the answer.**

- **0 tests.** No test file in `tests/` references `fleetlint`. The repo's most
  load-bearing tool, the one whose own docstring says *"the checks that would have caught
  tonight's defects"*, has no test file. There is no control available, so per the lane
  rule I report no mutation number for it.
- **Cannot run.** Every rule (`check_dead_exports`, `check_metadata`, `check_digests`,
  `check_fixture_trap`, `check_tests`) takes `repo, ref, token` and reads through
  `get_text()` → `api.github.com`. `python3 fleetlint.py SuperInstance/pong-quilt` →
  **`HTTP Error 401: Unauthorized`**. No `GITHUB_TOKEN` in this environment, and the API is
  rate-limited to 60/hr regardless.
- **Not in the wheel.** `pyproject.toml` ships `include = ["fleet_kit", "fleet_kit.*"]`.
  `fleetlint/` is **not packaged** — `pip install fleet-kit`, the documented install, does
  not deliver the linter.

A linter that flags everything and a linter that flags nothing are the same defect, and
right now there is no way to tell which this one is: no suite, no network in CI, not
installable.

**Verdict: COVERS THE PRODUCT** for the 51 runnable tests — the two mutations I could make
were both caught cleanly. The findings here are about *reach*, not about vacuity.

---

## 6. `quilt-tools` — VACUOUS

**Baseline: 94/94 self-checks green across all 11 tools, every one exit 0.** (The brief
says 113; the measured total is 94 — 7+6+7+8+8+6+7+9+8+9+19. The README's own table sums
to 94 as well.)

The README's central promise: *"everything here runs offline, **grades its own homework**,
and says so out loud… These are not demos wearing tool costumes."*

**Flagship: the grader itself.**

```
src/toolkit.mjs:77    export function check(name, ok, detail = '') {
src/toolkit.mjs:78      ok ? state.pass++ : state.fail++;
```

```js
export function check(name, ok, detail = '') {
  ok = true;   // MUTANT: the grader cannot fail
  ok ? state.pass++ : state.fail++;
```

**Result: 11/11 tools still green, 0 red.** The harness that produces all 94 self-checks
can be made unfailable and every tool still prints its green verdict line and exits 0.

**Controls — 1 of 3 caught, which is what makes this a finding and not a broken method:**

| # | control | `path:line` | result |
|---|---|---|---|
| 1 | `fnv1a64` returns a constant — the hash the whole witness chain is built on | `src/toolkit.mjs:45` | **SURVIVED — 11/11 green** |
| 2 | `verifyChain` → `if (false)` — **the tamper detector** | `src/toolkit.mjs:67` | **SURVIVED — 11/11 green** |
| 3 | `localEmbed` returns a zero vector — the retrieval geometry | `src/toolkit.mjs:136` | **CAUGHT — `ocean-recall.mjs` RED** |

Control 3 caught ⇒ the method is not inverted. Controls 1 and 2 surviving ⇒ the gap is real
and localised.

### `ledger-seal` is the sharpest instance

`ledger-seal` is billed as a *"tamper-evident append-only witness ledger, fnv1a-chained"*
and self-reports **6/6 green**. Its tamper detector is `verifyChain`. I instrumented it
with a stderr write and ran the tool:

```
=== verifyChain executions during ledger-seal's own run ===
        (no output)
```

**Zero.** The exported verifier — the function the product's headline claim is named for —
is executed **0 times** during the tool's own run, and replacing its entire body with
`if (false)` leaves the score at 6/6. A "tamper-evident" ledger whose tamper detection is
dead code, certifying itself green through a grader that cannot fail.

**Verdict: VACUOUS.** This is the `logtensor` class in its purest form, and it is worse in
one respect: `logtensor` at least ran its flagship line (it just never asserted on it).
Here the flagship is the *judge*, and the judge has no losing branch.

---

## What I would tell the orchestrator

1. **`pong-quilt` is the counter-example and should be treated as the fleet's bar.** Four
   flagship mutations, four catches, flagship line instrumented at 140.8M executions. The
   defect class is real but it is not fleet-wide — one repo in five came back clean.
2. **The defect has two species, and they need different detectors.**
   `voxelglyph` never runs the product; `quilt-tools` runs the product and grades it with
   an unfailable judge. A "does the test import the product" check catches the first. Only
   a mutation of the *harness* catches the second — and no repo in the fleet appears to
   mutate its own grader.
3. **Three of the five checkouts needed an environment repair before the baseline was
   meaningful** (GPG signing, hardcoded `/home/ubuntu` paths, pytest-only collection).
   A red baseline and a green baseline are both cheap to fake by accident. The lane rule
   "get it green first" is doing more work than it looks.
4. **Two repos have correct verification and no automation to run it.**
   `quilt-gpu-lab`'s receipt pin caught real drift and has no CI at all. `fleet-kit` ships
   a linter that is untested, needs a token, and is not in the wheel. Both are one
   `cron`/`workflow` away from being real.
5. **The 113 figure in the brief does not match the repo.** `quilt-tools` has 94
   self-checks, and its own README table sums to 94. If 113 came from somewhere, it is
   counting something that is not a self-check.
