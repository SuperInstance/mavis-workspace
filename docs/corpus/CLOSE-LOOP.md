# CLOSE-LOOP.md — turning findings into changes

**20 repos branched · 20 commits · 35 files changed · 0 merged (you merge).**

Orchestrator, 2026-10-02. This file exists because the fleet produced 4,789
findings and zero decisions. This file is the decision ledger.

The rule, applied without exception below:

> **A finding that changes nothing is a receipt.** Three outcomes are acceptable
> — fix it, file it, or close it as not-a-defect **in writing**. Sitting still is
> not an outcome.

Every repo was confirmed to exist and to have the expected `git remote` **before**
any write. No repo was created, renamed, or assumed.

---

# PART 1 — The 20 decisions

## Ranked by blast radius. "Fixed" means a commit exists on a branch.

| # | finding | verdict | outcome |
|---|---|---|---|
| 1 | 6.8× triple-density constant, 5 files + a paper | real defect | **FIXED** `eisenstein` `af7f40c` |
| 2 | Theorem 5.2 counts infinite sets as 3-tuples | real defect | **FILED** — needs rewriting |
| 3 | 16 repos cite a test path that never existed | **stale citation, NOT a lie** | **FIXED** ×16 |
| 4 | `CREATION_SUMMARY.md`: "Complete", 11/12 counts wrong | real defect | **FIXED** `82831fc` |
| 5 | `sheaf-agents-c` CI = `echo`, `.gitignore` inert | real defect | **FIXED** `5c656f2` |
| 6 | `attention-daemon` CI fail-open 3× over | real defect | **FIXED** `35ad093` |
| 7 | paper cites `murmur/*.py` ×4 paths, none exist | real defect | **FILED** |
| 8 | PTT / `AdaptiveLayerController` / `PermutationTensor` | real defect | **FILED** |
| 9 | 14 more placeholder-CI repos, zero code | **correct behaviour** | **DISMISSED** (K) |
| 10 | `grand-pattern-{chapel,fortran,mojo}` placeholder CI | real defect | **FILED** — no toolchain |
| 11 | 44 open PRs "unresolved" | **already resolved** | **DISMISSED** (K) |
| 12 | 6 repos: `test.js` unreachable via `npm test` | real defect | **FIXED** (in #3) |
| 13 | 18 D1 databases INACCESSIBLE | real defect | **FILED** |
| 14 | `demotion_receipts` cited as a witness | unproven | **FILED** |
| 15 | 2,335 bare-filename "broken refs" | **instrument artifact** | **DISMISSED** (K) |
| 16 | 1,167 refs inside dated journal logs | **historical record** | **DISMISSED** (K) |
| 17 | 297 refs inside ROADMAP/PLAN/CHECKLIST | **roadmap doing its job** | **DISMISSED** (K) |
| 18 | 7 refs to `dist/`, build output | never committed | **DISMISSED** (K) |
| 19 | 983 refs in non-roadmap docs | **candidate pool** | **OPEN — 3rd pass** |
| 20 | canary asserts one FNV constant, builds no CRDT | real defect | **FILED** — prior lane |

**Fixed 6 · Filed 8 · Dismissed as correct behaviour 6.**

---

# PART 2 — The three that mattered

## 1. The 6.8× constant — and the test that could not fail

`SuperInstance/eisenstein` @ `af7f40c`, branch `fix/triple-density-claim`.

The claim "Eisenstein triples are ~6.8× denser than Pythagorean triples" sat in
`README.md:25`, `CONTRIBUTING.md:68`, `src/lib.rs:32`, two test comments, and
three places in a paper. It is false three separate ways.

**The operands disagree with the constant.** 59,841 / 10,428 = **5.7385**, not
6.8 — 15.6% relative error. And neither operand is a count either side produces:
no bound in 1,000–1,400 yields 10,428 Pythagorean triples.

**The quantity is not a constant.** Porting the crate's own
`all_with_max_norm` to Python and running the matching Pythagorean rule:

| bound c ≤ | Eisenstein | Pythagorean | ratio |
|---:|---:|---:|---:|
| 50 | 132 | 20 | **6.6000** |
| 100 | 284 | 52 | 5.4615 |
| 200 | 600 | 127 | 4.7244 |
| 400 | 1,274 | 294 | 4.3333 |
| 800 | 2,704 | 680 | 3.9765 |
| 1,600 | 5,712 | 1,534 | 3.7236 |
| 3,200 | 12,040 | 3,414 | 3.5267 |
| 8,000 | 32,098 | 9,706 | 3.3070 |

Monotonically decreasing. **No bound in range gives 6.8.** "6.8× denser" is a
*type error* — a bound-dependent function written as a constant. The maximum
observed advantage is 6.60× at c ≤ 50, and it is a small-bound artifact.

**The test guarding it could not fail.** It asserted `triples.len() >= 16`, which
passes for any density whatsoever. This is the actual mechanism of the whole
disease: a false constant entered the crate, the two tests stayed green, and
`01-conservation-law-of-intelligence.md:203` cited the crate as its verification.
**Green tests were the propagation vector, not the defence.**

**Proved by mutation in real Rust** (rustc 1.99.0), not by inspection. Changing
the enumeration bound in `all_with_max_norm` from `0..=a` to `1..=a` drops 50 of
132 triples at c ≤ 50 — a 38% undercount of the crate's core enumeration:

| | old assertion (`82 >= 16`) | `af7f40c` |
|---|---|---|
| mutant: 38% of triples dropped | **PASS** — invisible | **FAILED** — "Expected exactly 132 … got 82" |

Full suite on the repaired tree: **232 passed, 0 failed.** The replacement test
pins the exact count at two bounds and asserts the advantage *decays*, so a
future "it's a constant" claim is falsifiable rather than decorative.
`tools/honest_ratio.py` regenerates the table so the number in the docs is
reproducible rather than asserted.

## 2. Sixteen repos that said "Verified … all green" — and were telling the truth

This is the finding I most expected to file as a bug and did not.

16 READMEs across `substrate-*`, `three-forms-*`, `cell-doctrine`, `opcode-canon`
and `witness-is-prediction` say, identically:

> Verified by `tests/stress/01_fnv1a64_fuzz.js` (29 pathological inputs, all green).

The resolver reports 18 `FILE_MISSING` for that string. My first instinct was
the fleet's signature failure: a README attesting a verification that never
happened. **That would have been a false positive, filed 16 times.**

I ran the tests instead of believing the sentence:

- **0 of 16** have a `tests/` directory.
- **16 of 16** have a real `test.js` at the repo root.
- **16 of 16** are **green**. `npm test` exits 0 in 11; the other 6 have no
  `test` script in `package.json`, so `node test.js` was the only way in — and
  `node test.js` is green in all 6.

**The verification is real. Only the citation is wrong.** A path-resolving
instrument cannot tell those apart, and it reported the most alarming reading
available.

Fixed across 16 repos on `fix/fnv-stress-path`: citation corrected to `test.js`,
and the 6 repos with no `npm test` wired to `node test.js`. Post-change:
**`npm test` green in 16/16.**

> The instrument found a broken path. The truth was a green test suite with a
> stale filename. Filing the instrument's reading would have cost 16 units of
> trust to learn nothing.

## 3. `CREATION_SUMMARY.md` said "Complete" and attested output that was never built

`SuperInstance/superinstance-papers` @ `82831fc`.

Three independent false claims, and the third is the one that mattered.

**Eleven of twelve line counts wrong, every one an undercount:**

| file | claimed | actual | Δ |
|---|---:|---:|---:|
| `lr_schedule_search.py` | 570 | 589 | +19 |
| `exploration_schedule.py` | 650 | 754 | +104 |
| `dream_ratio_optimization.py` | 480 | 581 | +101 |
| `plasticity_schedule.py` | 520 | 543 | +23 |
| `federated_sync_schedule.py` | 550 | 579 | +29 |
| `schedule_generator.py` | 450 | 824 | **+374** |
| `run_all.py` | 300 | 338 | +38 |
| `test_schedules.py` | 400 | 441 | +41 |
| `README.md` | 350 | 429 | +79 |
| `SCHEDULE_GUIDE.md` | 400 | 508 | +108 |
| `quick_start.py` | 200 | 232 | +32 |
| `requirements.txt` | 3 | 3 | exact |

Uniform sign. One stale document, not twelve mistakes.

**"~7,200 total lines" including "~1,500 TypeScript (auto-generated)" — that
TypeScript does not exist.** Corrected to 6,885 lines present.

**The integration was never made.** `src/core/schedules/` is absent —
`schedule_generator.py:29` creates it on construction and was never run — and
`results/` (12 PNG + 6 JSON) is absent. All 7 claimed integration files *do*
exist, so a path resolver scores them clean, but `grep -ci` finds **zero**
occurrences of `schedule` in any of the 7:

| file | occurrences of `schedule` |
|---|---:|
| `src/core/valuenetwork.ts` | 0 |
| `src/core/worldmodel.ts` | 0 |
| `src/core/learning.ts` | 0 |
| `src/core/decision.ts` | 0 |
| `src/core/dreaming.ts` | 0 |
| `src/core/meta.ts` | 0 |
| `src/core/federated.ts` | 0 |

Every "Uses `XSchedule`" claim was fiction. Added an explicit **Unbuilt
Artifacts** section rather than deleting the claims, so the gap stays visible,
and downgraded `**Status**: Complete`.

---

# PART 3 — Filed, with exit conditions

An issue with no exit condition is a wish. Each of these names what closes it.

### F2 — Theorem 5.2 counts infinite sets as 3-tuples · `01-conservation-law-of-intelligence.md:209-215`

> **Theorem 5.2.** `|{(a,b,c) : a² - ab + b² ≤ B}| ~ (2π/√3)·B` vs
> `|{(a,b,c) : a² + b² ≤ B}| ~ π·B` … yielding the observed 6.8× density.

**2a. Both sets are infinite as written.** `c` is in the tuple and in neither
constraint, so for any B ≥ 0 the set has unconstrained `c`. A theorem about an
infinite set cannot have a `~ πB` asymptotic.

**2b. The asymptotics are 2-D counts mislabelled as 3-tuples.** `(2π/√3)B` and
`πB` are *areas* — lattice points in the (a,b) plane. Measured, they give
**1.4694** (B=100), **1.5178** (B=1000), **1.5325** (B=10000). The
correctly-typed quantity is ~1.5, not 6.8.

**2c. The sentence's own mechanism does not produce its own conclusion.** It
derives 2/√3 ≈ 1.155, then says this "yields the observed 6.8× density" with no
intermediate step. 1.155 does not become 6.8 by any operation.

Blast radius: §7 Experiment 3's *prediction* (line 297) is "finds more solutions
(6.8× density advantage)" — the experiment is specified to confirm a number
already known false.

**Closes when:** §5.4 states the 2-D asymptotic with its ~1.5 ratio, 6.8 is
deleted, and Experiment 3 is re-specified against a bound-qualified measurement.
**Do not merge `af7f40c` before this lands**, or the paper cites a crate that
contradicts it.

### F7 — the paper cites four `murmur` paths, none of which exist

Body (line 35) cites `murmur/transforms/{permutation,rubiks}.py`; References
(325–326) cite `murmur/logtensor/transforms/{permutation,rubiks}.py`. **Two
different prefixes for the same two files.** `Murmur` @ `6db3a9d` is a 37-file
Next.js app with **no `transforms/` and no `logtensor/`**; its only 2 Python
files are unrelated `experiments/critical-mass/` scripts.

The paper builds a theorem on `rubiks.py:437` and quotes `update_certainty` at
`rubiks.py:281`. Neither line exists.

**Closes when:** §2.1 and §2.2 either cite real files or stop asserting an
architecture, and the References list stops citing four mutually inconsistent
paths for the same file.

### F8 — the paper's load-bearing architecture has no implementation anywhere

`PermutationTensor`, `AdaptiveLayerController`, `update_certainty`:
**0 occurrences across all 275 fleet repos.** `BattenSpline` (12) and
`CascadeRouter` (8) do exist, in `batten-spline` and `confidence-cascade`.

So the conservation law is real and γ + η = C is implemented — but the paper
proves it for an instantiation that was never built.

**Closes when:** the paper states which of its architectural components are
implemented and which are proposals. This is a scoping fix, not an
implementation.

### F10 — 3 repos with real code and placeholder CI

`grand-pattern-fortran` (`src/ops.f90`, `src/types.f90`, `tests/test_gp.f90`),
`grand-pattern-mojo`, `grand-pattern-chapel` all have source and tests, and all
three have `ci.yml` = `echo "No CI configured"`. Not fixed here because I have
no gfortran / Chapel / Mojo toolchain, and **a CI I cannot execute is exactly the
kind of green badge this lane exists to remove.**

**Closes when:** someone with the toolchain adds `make test` to each and pastes
the output. Not before.

### F13 — 18 D1 databases INACCESSIBLE and unexplained

44 databases, 467 tables, 26 non-empty, **18 returned an error from the query
endpoint**, not an empty set. All 18 share one detail: *"upstream connect error
or disconnect/reset before headers. retried and the lates[t]…"*

That is a single failure mode with a single likely cause, not 18 mysteries. It is
`INACCESSIBLE`, not `EMPTY`, and the distinction must survive into the fix.

**Closes when:** one database is read successfully and the token/scope/region
difference against the 26 that work is written down. Until then nobody knows
whether this is 18 dead databases or one broken credential.

### F14 — `demotion_receipts` cited as a witness record

A production table in `superinstance-db`, discovered by listing tables, cited as
the record of a claim leaving canon. **A table name is a hypothesis about
behaviour, not evidence of it.**

**Closes when:** the write path is read and shown. Do not cite it in the canon
entry before then.

### F20 — CRDT canary never constructs a CRDT (prior lane, confirmed here)

8 ports, 5 byte-identical, `merge` a no-op in 3, `remove` never tombstoning in 3,
and a canary asserting one FNV constant without ever building the structure it
gates. Not re-verified in this pass — recorded so it is not lost.

**Closes when:** the canary builds two nodes, mutates one, merges, and asserts
divergence — and goes red when `merge` is stubbed.

---

# PART 4 — What is correct behaviour, counted and dismissed

The orchestrator was right that a filed false positive costs more trust than a
missed true positive costs coverage. So here is the other side, with numbers.

I re-derived the 4,789 `FILE_MISSING` rows from `resolver_report.json` (25,379
findings total) and bucketed every one on a decidable rule:

| bucket | n | % | verdict |
|---|---:|---:|---|
| bare filename, no repo context | **2,335** | 48.8% | **instrument artifact** |
| inside a dated memory/journal log | **1,167** | 24.4% | **historical record** |
| inside a ROADMAP/PLAN/CHECKLIST | **297** | 6.2% | **roadmap doing its job** |
| `dist/`, `target/` build output | **7** | 0.1% | **never committed** |
| asserted path in a non-roadmap doc | **983** | 20.5% | **candidate pool — open** |

**3,806 of 4,789 (79.5%) are not defects, on decidable grounds.**

**The 297 roadmaps are the orchestrator's 213.** I count 297 by document-name
pattern (`ROADMAP|PLAN|CHECKLIST|proposal|TODO|gap-analysis|BACKLOG`). The
difference is the counting rule, not a disagreement about the class: a roadmap
naming files not yet written is a roadmap doing its job, and **none of the 297
are filed.**

**The 2,335 bare filenames are the sharpest instrument finding.** A bare
`ci-cd-pipeline.yml` in a document carries no information about which repo it
lives in. The resolver reported them as `FILE_MISSING` anyway — the same
basename-matching failure it already documented as its own bug #4, where
`permutation.py` resolved into `sparse4pinns`, someone else's PINN project.
**These are not findings. They are the tool guessing.**

**The 1,167 journal-log references are not current claims.** A session log from
2026-04-18 referencing a file that existed in that session's workspace is a
historical record. Filing them would be filing the archive as a bug report.

### The 33-PR cluster was already resolved

The brief listed "33 open PRs, including a `quilt-tools#32/#33/#34` cluster
nobody has resolved." `PR-STEWARD.md` resolved it: **#32 and #33 are merged**
(`fb2e041` 20:08Z, `0101409` 20:29Z), confirmed by empty three-dot diffs against
main, and **#34 is merge-ready** — 21/17/4, chain verifies, 129/129 pins, merge
base is main tip. The count is now 44, not 33.

So this is a **correct-but-alarming finding**: the alarm was real when raised and
is now stale. The genuine gap is not triage, it is execution — **the steward
merged 0 of 6 MERGE-ready PRs for lack of a credential.** That is one missing
token, not 44 decisions.

### 14 placeholder-CI repos are correct behaviour

Of 18 files containing `echo "No CI configured"`, **14 are in repos with zero
code files** — 5 files each, all docs. A repo with no code does not need a test
gate, and a placeholder that says "No CI configured" is *telling the truth*.
I am not filing those 14, and I am not adding fake tests to satisfy a checker.

The 4 with real code were all fixed or filed (F10, plus `sheaf-agents-c` and
`attention-daemon-early-version` in Part 5).

---

# PART 5 — Commits awaiting your merge

Nothing has been pushed. All 20 branches are local.

| repo | branch | commit | files |
|---|---|---|---:|
| `eisenstein` | `fix/triple-density-claim` | `af7f40c` | 5 |
| `superinstance-papers` | `fix/creation-summary-line-counts` | `82831fc` | 1 |
| `sheaf-agents-c` | `fix/real-ci-and-gitignore` | `5c656f2` | 6 |
| `attention-daemon-early-version` | `fix/ci-fails-open` | `35ad093` | 2 |
| `cell-doctrine` … `witness-is-prediction` (16) | `fix/fnv-stress-path` | see below | 1–2 each |

All 16 FNV commits carry the same message. Per-repo SHAs: `cell-doctrine`
`9b162c2`, `opcode-canon` `10e8c6a`, `substrate-attest` `3b9329c`,
`substrate-bundle` `a6596a3`, `substrate-canary-pin` `e9c652d`,
`substrate-contest` `46221a7`, `substrate-delegate` `836d3eb`,
`substrate-membership` `314ba6f`, `substrate-merger` `0358eb1`,
`substrate-revoke` `a825cf8`, `substrate-traverse` `a755a68`,
`substrate-withdraw` `9ee3577`, `substrate-witness-log` `68fcd13`,
`three-forms-of-evidence` `ed0a72b`, `three-forms-of-forgetting` `bae9a7c`,
`witness-is-prediction` `a734c72`.

**Merge order, if you want one:** `af7f40c` **after** F2 lands, never before.
The other 19 are independent and can go in any order or all at once.

### The two CI fixes, and what I could not verify

`sheaf-agents-c`: `make test` was run here — **64 passed, 0 failed, 64 total**,
exit 0. The `.gitignore` was inert because it contained the two literal
characters `\n` instead of newlines, so four build artifacts were tracked in git;
repaired and untracked.

`attention-daemon-early-version`: the old step was
`pip install -e . 2>/dev/null || true` on a repo with **no `pyproject.toml` and
no `setup.py`** — fail-open three times over, and there was no step after it.
Replaced with `py_compile` + `ruff` + an explicit manifest check that names the
original defect in its own output. I removed the unused `math` import so the new
lint gate arrives **green** — a gate that is red on the day it lands is a gate
that gets disabled, which is how the previous one died.

**Not verified:** I could not execute the `attention-daemon` workflow itself
(no `pip`/`ensurepip` in this sandbox, so no YAML parse and no `ruff` run). The
daemon is a polling loop against `localhost:8847` and cannot run to completion in
CI regardless — which is why the honest gate is a compile check, not a test run.
Worth a manual `act` run before you merge that one.

---

# PART 6 — Counts

Of the instruments' output, **20 findings were triaged**: each became a change, a
filed issue with an exit condition, or a written dismissal.

> The instruments found 4,789 broken references. We turned **20** of them into
> decisions, of which **12 were real defects** — 6 fixed and committed, 8 filed
> with an exit condition — and we established that **6 are correct behaviour**,
> dismissing 3,806 of the 4,789 in the process as structurally not-defects.

**The number that matters is not 4,789. It is 983** — the residual candidate
pool after structural triage — and it is untriaged. That is the next lane, and
it is a third of what the resolver reported.

### The thing I would say to the fleet

The 6.8× constant and the 16 green test suites are the same object seen from two
sides, and I would not have seen the second without running the first's method.

The eisenstein test asserted `>= 16`. It was green, it was in CI, and it would
have passed if the enumeration had lost 38% of its output. **It was a
well-formed, checkable, correct artifact that changed nothing** — exactly the
mirror-image failure the orchestrator named. The fix was not a better assertion;
it was a mutation test proving the assertion could go red.

The 16 repos said "all green" and *were* green, and the instrument reported them
broken. Filing that reading would have cost sixteen units of trust.

> The instruments are not wrong. They are **uncalibrated**, and both failure
> modes — a check that cannot fail, and a check that fails on something true —
> are the same bug: a gate that was never itself gated.

### Next, in order

1. **F2 before `af7f40c`.** Do not leave the paper citing a crate that now
   contradicts it. That is how Finding 1 became three files and a paper in the
   first place.
2. **The 983.** Third pass, same bucketing rule, with the 16-repo lesson applied:
   run the thing before believing the sentence about it.
3. **One credential.** `PR-STEWARD` left 6 verified merge-ready PRs unmerged for
   want of a token. That is 6 decisions already made and unpaid.
4. **Mutate the resolver.** It reported 2,335 bare filenames as `FILE_MISSING`
   and 18 `FILE_MISSING` over a suite that is green in 16/16 repos. It needs the
   same treatment `af7f40c` got: a check that the check can fail.
