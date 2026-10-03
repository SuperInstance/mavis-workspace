# CI LANE — make the fleet's good work prove it runs, on every commit

**Lane:** `ci` · **Date:** 2026-10-01 · **Base:** `ci-production-sweep` branches, nothing pushed.
**Artifacts:** `canfail.py` (this dir) · `connect4/ci/` + `.github/workflows/ci.yml` ·
`ga4444/ci/` + `.github/workflows/ci.yml`

---

## 0. The brief's headline number is false, and the instrument is why

> Brief: *"17 first-party autopublishers exist, 11 of them have no tests at all."*

**"11 of 17 have zero tests" is a bug in `triage.py`.** `triage.py:40-41,112-117`:

```python
SRC  = re.compile(r"\.(py|ts|js|rs|go|jl|hs|ml|ex|exs|c|cpp|h|java|rb|swift|kt|scala)$")
TEST = re.compile(r"(^|/)(tests?|spec|__tests__)(/|$)|_test\.|test_.*\.py$|\.test\.|Test\.java$")
if   SRC.search(p): row["src"]  += 1
elif TEST.search(p): row["test"] += 1     # <-- UNREACHABLE
```

`SRC` is a bare extension match, so it wins on every test file in this fleet. Measured on
7 representative paths, **6 of 7 are swallowed** and `TEST` counts 0 forever. The
`untested` signal in `triage.json` (338 of 500 repos) is an artifact and must not be cited.

`AUTOPUBLISH.md` already recounted all 17 by executing them: flux-runtime **2755**,
usemeter 2079, websocket-fabric 321, ccc-os 236, flux-js 172, quilt-fleet 148.

> **The real defect is worse than "no tests": tests exist and never run on the release
> path.** And the structural reason is sharp — **GitHub Actions does not gate across
> workflows.** Each repo's `ci.yml` runs on `push: branches:[main]`; not one runs on a tag
> push, and not one can block a tag-triggered publish. The green checkmark on `main` has
> protected **zero** releases in this fleet.

---

## 1. Census — CI that cannot fail

`canfail.py`, run over every workflow in the 275 local clones. **Ranked by current-tree
content; GitHub's `size` field was never read.**

| | |
|---|---|
| workflow files scanned | **174** |
| **cannot fail** | **23 (13.2%)** |
| unparseable (recorded, never "clean") | 2 |
| repos with ≥1 CI file | 105 |
| **repos with a cannot-fail CI** | **22** |

Breakdown of the 23: **18 are placeholders** — `run: echo "No CI configured — customize per
project requirements"` (15 `cocapn-*`, 3 `grand-pattern-*`); 1 is `pip install -e . 2>/dev/null
|| true` as its only step (`attention-daemon-early-version`); 5 are release-automation
workflows with no test step (`axum/release-plz.yml` et al.).

Two spots checked by hand, both true positives:
- `cocapn-abyss/…/ci.yml` — the file is literally one line: `- run: echo "No CI configured"`.
- `attention-daemon-early-version/…/ci.yml` — one step, `|| true`.

**First-party vs forked:** the 174 files are all in `repos/`, the fleet-triage clone set.
`connect4`, `ga4444`, `fleet-kit` are first-party `SuperInstance/*`, confirmed by
`git remote -v` before any write. **No GitHub pushes were made.**

---

## 2. `connect4` — CI added, and a live regression repaired

`ci/verify.sh` already existed and is a **good gate**: builds, asserts both known-answer
checks by exact text, regenerates the export, pins FNV-1a, asserts the committed file is
untouched. It was **untracked and invoked by nothing.** That was the whole gap.

### The artifact is intact

```
connect4/c4_ground_truth.txt   computed=0x4ef8351a5c319637  claimed=0x4ef8351a5c319637  MATCH
ga4444/gt4444_ground_truth.txt computed=0xcdc9636c704a7ba2  claimed=0xcdc9636c704a7ba2  MATCH
```

Both digests independently recomputed in Python. `connect4` 54,166 rows; `ga4444` 3,338.

### A >900× regression was sitting in the working tree, uncaught

An uncommitted edit flipped one sign:

```c
- if (has_won(pos | t, mask | t)) return  1 << 20;   /* winning move, take it */
+ if (has_won(pos | t, mask | t)) return -(1 << 20);
```

The insertion sort at `ctool.c:143` is **descending**, so `1 << 20` searches winning moves
FIRST — as the comment says. The flip sends them **last**.

| tree | sign | parens | `verify.sh` | elapsed |
|---|---|---|---|---|
| HEAD | `+1<<20` | ✗ | **FAIL** — new `-Wparentheses` warning | 2s |
| working tree (as found) | `-(1<<20)` | ✓ | **FAIL** — and **>900s** | >900s |
| **repaired** | `+1<<20` | ✓ | **PASS** | **1s** |

The working tree had also had `c4_ground_truth.txt` truncated to 7 rows to make it finish.
**Repaired**: sign restored, parenthesisation kept, dataset restored from HEAD.
`verify.sh` now exits 0 in 1 second. `git diff` shown at the end of this document.

### `c4.py` cannot be gated the way the brief assumes — measured

`c4.py`'s docstring says **"negamax with alpha-beta"**. There is no alpha and no beta
parameter — `inspect.signature` is `(b, turn, depth=11)`. Node growth on the empty board:

```
depth 2 →     57 nodes   0.01s
depth 4 →  1,415 nodes   0.25s
depth 6 → 22,100 nodes   2.86s     (~7,700 nodes/s, ~10× per 2 plies)
```

`MAX_PLY = 11` extrapolates to ~8M nodes ≈ **17 minutes for one position**. So a
cross-check of the Python solver against the 54,166-row ground truth is not possible inside
a CI job, and it is not merely omitted for convenience. Measured: on the 7 ply-1 positions
the C labels `-1`, and `c4.py` at depth 4 returns `0` on all 7 — **0/7 agreement**, because
`ctool.c` solves to full depth (42 plies) and `c4.py`'s horizon value is an upper bound.
A cross-check there would report a horizon difference as a correctness failure.

### The suite: 12 checks, 4/4 mutants killed

`ci/test_c4_vs_truth.py` — pins horizontal, vertical and diagonal forced wins, a full
column not being legal, `immediate_wins` behaviour, and the **horizon line** itself
(`depth 1` on a fork must report `0`, not a fabricated win). It also asserts that
`negamax` **was entered** (call counter), so the value assertions cannot pass vacuously.

| mutant | result |
|---|---|
| `return best` → `return best * 0.0` | **caught** (exit 1) |
| vertical win detection disabled | **caught** (exit 1, 2 checks red) |
| `if depth <= 0: return 0` → `return 1` | **caught** (exit 1) |
| early-exit on win inverted | **caught** (exit 1) |

Two of these **survived the first version** and were only killed after the missing
positions were added. The vertical mutant survived because every position was horizontal;
the horizon mutant survived because no assertion was *decided* by the horizon line. That is
the whole argument for running mutants instead of counting passes.

---

## 3. `ga4444` — the ground truth is wrong on 74% of its own rows

This is the lane's sharpest finding.

`ga4444.py` plays **free placement** — `legal_moves()` returns every empty cell, and its own
docstring warns a column-only enumerator "would silently shrink the dataset".
`gt4444.c` plays **column-only**: `height_of(b,c) = __builtin_popcount(column)` and
`top()` places at row `popcount`. On a column with a gap the new bit lands on an **occupied
row**, and because it is `+` and not `|`, the carry rewrites an existing stone:

```
column 0 before   0b0101   (rows 0 and 2, gap at row 1)
height_of        2        → place at row 2, already occupied
b + (1 << 2)     0b1001   (rows 0 and 3 — the row-2 stone TELEPORTED)
```

The export enumerates free-placement positions anyway. Measured on the shipped file:

> **2,484 of 3,338 rows (74.4%) carry a gap under a stone** — positions the search is not
> defined on. On a sample of those, `gt4444 --probe` and `ga4444.py` **disagree on 49/150
> (32.7%)** and **10/25 (40.0%)** at the CI sample size.

### Why `verify.py` still reports 2000/2000 PASS

Its position generator has the same column-only rule:

```python
for c in range(W):
    for r in range(H):
        if not (a & mbit(r, c)) and not (b & mbit(r, c)):
            cand.append((r, c)); break      # ← break: column top only
```

So the differential compares two column-only solvers on column-only positions. **That
result is sound — for the column-only game — and it says nothing about the 74% of the
dataset that has gaps.** A green differential is not the same claim as a correct dataset.
`ci/test_ga4444.py` bounds this explicitly and asserts the `break` is still there.

### Two more controls that cannot fail

- `verify_maxmin.py`'s three sanity cases are **`print()` only — no assertion, exit 0**. One
  prints `+0` beside the text `(expect -1, B takes the fourth)`, and the script still exits 0.
- `truth.py` in `connect4` is **dead code**: written against the old bitboard API
  (`c4.BOARD`, `c4.can_play`, `negamax(p0,p1)`), none of which exist. It raises
  `TypeError: wins() missing 1 required positional argument` on first use.

`ci/test_ga4444.py` (11 checks) pins the digest, the 2,484 gap count, the carry mechanism,
the blindness of `verify.py`, the draw, and the disagreement rate — **green while the
repository is known broken**, because a red gate nobody can fix is a gate people disable.
Pinning the defect as a measurement means a *fix* shows up as the number moving.

---

## 4. `fleet-kit` — verified NOT vacuous

The brief asked me to check this. It passes on every axis:

- **7/7 workflows can fail** (`canfail.py` clean); main workflow has **9 gate steps**;
  **no `|| true`, no `continue-on-error`** anywhere.
- It asserts its own instrument is honest: the full-run step requires `rc -eq 3` and
  `complete is False` with `L1,L4 ∈ skipped`. A run that quietly claimed completeness fails.
- It runs `fleetlint --selftest` **before** the suite, and installs into a clean venv.
- **186 tests pass in 6.5s.** The suite references every rule (L1–L9, M1–M2) and imports
  real product modules — not the `load-is-not-ok` pattern.
- **Mutation:** neutering the L6 digest-preimage rule →
  `FAILED tests/test_fleetlint.py::TestDigestPreimage::test_fires_on_latin1`, exit 1.

**One latent weakness, not a current defect:** `ci.yml:92` is
`test -d "$(... fleetlint --templates | head -1)"` — a pipe with no `set -o pipefail`. The
`test -d` still gates so the step *can* fail, but if the producer errored the substitution
yields an empty string and `test -d ""` fails for the wrong reason. Worth `set -o pipefail`.

---

## 5. The rule — `canfail.py`, with negative controls

Asks the only question that matters: **if the product were wrong, would this go red?**
Per **step**, never per file — a prior audit found the per-file version lets one
`set -o pipefail` exempt every other job in the same file. It also models that **each `run:`
is a separate shell**, so the guard does not cross steps.

```
$ python3 canfail.py --selftest
  [ok ] good: plain test run                        expect_fire=False  got=False
  [ok ] bad:  producer | tail -1                    expect_fire=True   got=True
  [ok ] good: pipefail in the same step              expect_fire=False  got=False
  [ok ] bad:  echo only                              expect_fire=True   got=True
  [ok ] bad:  continue-on-error                      expect_fire=True   got=True
  [ok ] bad:  || true                                expect_fire=True   got=True
  [ok ] bad:  uses-only                              expect_fire=True   got=True
  [ok ] good: mixed file (file can fail; 1 job flagged)
  [ok ] per-step trap         expect_fire_on_step=[2]  got=[2]
  [ok ] per-file: one guarded, one not   expect=[unguarded]  got=['unguarded']
SELFTEST PASSED — fires on 6 of 6 always-green shapes, silent on 2 real gates.
```

**Negative control against the real thing, as required — it does not fire on the new CI:**

```
$ python3 canfail.py .../connect4/.github/workflows
[  can-fail]  ci.yml   jobs=1 gate_steps=4     1 workflow: 0 cannot fail    exit=0
$ python3 canfail.py .../ga4444/.github/workflows
[  can-fail]  ci.yml   jobs=1 gate_steps=5     1 workflow: 0 cannot fail    exit=0
```

**The controls found three real bugs in the checker itself**, which is the argument for
having them:

1. `_split_top` compared a **2-char slice against a 1-char separator set**, so it never
   split on a single `|` — the pipeline check, the entire point of the tool, was dead.
2. Fixing that surfaced the inverse: with `seps="||&&;"` a **lone** `|` is a *member* of the
   set and split `./build.sh | tail -1` into two harmless commands. Replaced the character
   set with explicit operator strings, longest-first.
3. A case where the **test's own expectation was wrong** — a file with one guarded and one
   unguarded job *can* fail at file level. The per-job verdict belongs to a separate
   assertion, and conflating them is how a per-file checker reports a clean bill of health
   for a half-inert file.

### `pipefail` discipline in everything added

Every `run:` block in both new workflows begins `set -euo pipefail`. No gate reads through
a pipe. Artifact checks use `grep -Eq` against a redirected file and `test "$rc" -eq 3`
against a captured status, never `$?` after a pipe.

---

## 6. CPU / CUDA

**No GPU was used, and none is claimed.** Every number in this document was produced on
CPU in this sandbox: C via `cc -O3 -std=c11`, Python via CPython 3.11. `ga4444/run.py`
touches `numpy` for a linear-model baseline, which is CPU. Nothing here is or claims to be
a GPU result. `connect4` and `ga4444` have no CUDA path at all.

---

## 7. What I changed, and what I did not

**Written locally, nothing pushed** (per the hard rules):

| path | what |
|---|---|
| `fleet-triage/canfail.py` | the checker + 10 negative controls |
| `prod/connect4/.github/workflows/ci.yml` | **new** — runs the gate that existed but was never invoked |
| `prod/connect4/ci/test_c4_vs_truth.py` | **new** — 12 checks, 4/4 mutants killed |
| `prod/connect4/ctool.c` | **repaired** — sign restored |
| `prod/connect4/c4_ground_truth.txt` | **restored** from HEAD (7 → 54,166 rows) |
| `prod/ga4444/.github/workflows/ci.yml` | **new** |
| `prod/ga4444/ci/test_ga4444.py` | **new** — 11 checks, pins the 74% defect |

**Deliberately NOT changed:**

- `ga4444/gt4444.c` — the carry bug is a real product defect. Fixing it changes the
  published ground truth, so it is a decision for the repo owner, not a CI lane.
- `ga4444/verify_maxmin.py`'s print-only sanity cases — same reason.
- `connect4/truth.py` — dead against the old bitboard API; rewriting it is a design call.
- `triage.py`'s `if/elif` — the census fix is the first item on the lane list and gates
  every downstream number; it is not a CI change and should not ride along in this diff.

**Open, and worth a decision:** 18 of the 23 cannot-fail files are `echo "No CI configured"`
placeholders in repos that are otherwise ordinary. Those are one workflow file away from
being either real CI or honestly absent.
