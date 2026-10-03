# PLAYTEST2 — the detector, and the three I left open

**Lane:** playtester. **Date:** 2026-10-01. **Round:** 2.

**Nothing was fixed.** No repo mutated on disk, no commits, no pushes. All five checkouts
are at their original HEADs. Where I constructed a failing state I did it in a throwaway
copy and deleted it. The one thing I *did* write is a new tool, in a new directory.

Working copies: `playtest2/{quilt-tools,quilt-gpu-lab,voxelglyph,pong-quilt,fleet-kit}`,
plus `playtest2/vg-prefix` (voxelglyph at `8eb8eec~1`, the pre-fix control) and
`playtest2/exectest.py`.

---

## The number you asked for

> how many of the fleet's repos have a suite that executes its own product

**8 of 275 repos examined — and that 275 is a biased sample, detailed in §5.**

Of the 8: every mechanical mutation I could construct was caught. That is a *floor*, not
a count of good repos. Here is the whole ledger, because the denominator matters more
than the numerator:

| verdict | count | what it means |
|---|---:|---|
| **PROVEN** — every mutation caught | **8** | `cell-doctrine`, `madlibs-gan`, `madlibs-gan-npm`, `micrograd-quilt`, `quilt-bandit`, `three-forms-of-evidence`, `three-forms-of-forgetting`, `witness-is-prediction` |
| PARTIAL — some mutations survived | 1 | `quilt-cell` (1/3) |
| **VACUOUS** — every mutation survived | **13** | 10 × `substrate-*`, `scrap-voice`, `recovered-copy-20260824-scrap-voice`, `fleet-static-host` |
| UNRESOLVED — ALREADY-RED or COULD-NOT-RUN | 51 | red at HEAD, or no usable runner |
| NO SUITE AT ALL | 202 | no file matching test conventions |

**The honest headline is the ratio: of 22 repos where I could run a mutation experiment
at all, 13 let the product break silently. That is a 59% survivor rate.** `voxelglyph`
and `quilt-tools` — the two I hand-audited last round — are *not* in this table, because
neither is in the 275-repo sample. I ran them by hand and they are in §1 and §2.

---

## 1. `quilt-tools` — where the grading is unfailable

**Baseline: 94/94 green, all 11 tools exit 0.** (The brief says 113; measured 94, and
the README's own table sums to 94. Third time I've measured this.)

I parsed all 94 `check()` call sites with a balanced-paren scanner and ran a
statically-always-true detector over each assertion expression. **Exactly one is
unfailable.**

### The exact place

```
tools/budget-tide.mjs:112
  check('no negative-amount loophole',
        r3.refused === true || r3.ok === false || r3.amount > 0 || true,
        'refusal is by budget math, amount sign irrelevant here');
                                                                              ^^^^^^^
```

The final disjunct is the literal `true`. I evaluated the expression over six values of
`r3` — normal accept, refuse, a "loophole" accept with a negative amount, an all-false
object, and an empty object. **It returns `true` for every one.** The only way to make it
not-true is to throw.

This is a different defect from the one I reported last round, and it is worse in one
respect: **it needs no mutation to be unfailable.** Last round I had to edit
`src/toolkit.mjs:77` to make the grader unable to fail. This one is unfailable in the
committed tree at `main`, and the tool named `budget-tide` prints `8/8 checks green`.

The check's own `detail` string is honest about it — *"amount sign irrelevant here"* — so
the author knew the assertion was vacuous and shipped it under a name that claims
otherwise. That is the shape of the whole defect class: **the prose admits what the
predicate denies.**

### What it would take to make it able to fail

The product is at `tools/budget-tide.mjs:53`, the `money.spend` program cell:

```js
if (env.spent >= env.budget)
  return { refused: true, reason: ..., short_by: amount };
await runtime.set(cell, { ...env, spent: env.spent + amount });
```

`spend('dining', -5, ...)` is called at line 111 with a negative amount. Because the
envelope is dry at that point, the gate refuses before the sign is ever consulted — so
`r3.refused === true` happens to hold. **The guard is not the predicate; the predicate is
decorative.** Four assertions could replace it, in increasing strength:

1. `r3.refused === true` — states the actual fence the product implements. Would fail the
   moment the gate moved.
2. `r3.refused === true || r3.spent <= budgetBefore` — survives a *correct* fix that lets
   a refund legitimately reduce `spent`, and still fails a loophole.
3. A metamorphic pair: spend `-5` and assert the envelope's `spent` afterwards equals its
   prior value. This is the strongest and the one I would ship — it asserts on *state*,
   not on a return code, so no amount of refactoring the response shape defeats it.
4. Drop the check. **A check that cannot fail is worse than no check**, because it
   occupies the slot where a real one should be. This is the cheapest correct answer.

### But that is not the interesting unfailability

One tautology out of 94 is a defect, not a *detector gap*. The thing you actually asked
about is the harness. Re-measured on this tree:

```
src/toolkit.mjs:77    export function check(name, ok, detail = '') {
src/toolkit.mjs:78      ok = true;   // MUTANT
src/toolkit.mjs:78      ok ? state.pass++ : state.fail++;
```

**Result: all 11 tools still print their green verdict line and exit 0.** Every one of the
94 numbers is produced by a function with no losing branch. And there is **no test of the
harness anywhere in the repo** — I grepped for any reference to `toolkit` outside
`src/` and every hit is a consumer, never a test. The CI workflow
(`.github/workflows/ci.yml`) runs `npm run check` (a syntax check), `fleet-pager` (one of
eleven), and the GAN verify scripts. **It never runs the other ten tools and never runs
`check()` against a deliberately-false assertion.**

### On your format-vs-semantic hypothesis

You said: *if the 94 checks are mostly "this row parses and has the fields it had before,"
that is a format check masquerading as a semantic one.*

**I tested this and the hypothesis is wrong for `quilt-tools`.** Reading all 94
assertions against the product logic, the large majority assert on **decisions**, not
shape:

- `convergence-gauge:190` — `r1.verdict === 'CONVERGED' && r1.flat_tail_len >= 8`
- `driftwatch:115` — `r3.label === 'oscillating'`, on a series whose *mean is healthy*
- `driftwatch:107` — `driftFlaggedAt > naiveFiredAt`, i.e. it asserts the tool beats a
  static threshold, and it prints the lead time
- `convergence-gauge:223` — `r4.change_points.length === 1 && cp >= 14 && cp <= 16`
- `ocean-recall:107` — `r3.hit === false`, an *absence* must be reported
- `pipeline-guard:136/138` — a schema relaxation admits one row and still dead-letters four

These are CUSUM change-point positions and hysteresis flip counts. They cannot be
satisfied by a row that merely parses. **The `quilt-tools` defect is not format-instead-of-
semantics; it is that the grader itself has no failure branch, plus one decorative
predicate.** That is a different species from `voxelglyph`'s, and it needs a different
detector — you were right about that, and §4 is that detector.

### One correction to my own last-round report

I wrote that `verifyChain` is *"executed 0 times during `ledger-seal`'s own run"* and
implied the tamper detection was dead code. **That was wrong in its implication.**
`ledger-seal` does not use the exported `verifyChain` at all — it defines its own copy
*inside the sheet* as the `ledger.verify` program cell (`tools/ledger-seal.mjs:60-79`),
and calls it via `e.call('ledger.verify')`. So my instrumented export saw zero executions
because nothing calls it; the product's real verifier runs, and it correctly pins
`v1.brokenAt === 2` on a tampered row. **The tamper detection is real and is tested.** The
duplicate implementation is a maintenance hazard, not a vacuity. I should have read the
call site before writing "dead code."

---

## 2. `quilt-gpu-lab` — the seal does not describe the tree it seals

**HEAD has moved since last round: `20ba1c9 re-seal manifest after SCOUT-9 ledger change`.
It is GREEN. 6/6.** Last round's `ALREADY-RED` was real and has been fixed upstream — the
re-seal did its job. So the first of your two questions has a clean answer: **nothing is
red, and it is not red because of the rebase.**

Which leaves the second question, and yes — **I constructed the case you hoped I
couldn't.**

### The seal binds no git identity

`tools/receipt_manifest.py:63-86` (`build()`) emits six keys: `schema`, `generated_at`,
`doctrine`, `ledgers`, `experiments`, `tools`. No commit. No tree. No branch. No parent.
The manifest is content-addressed only, and `test_receipts.py:88-107` compares exactly
`ledgers`, `experiments`, `tools`.

### Stale manifest, guard green — demonstrated

**Construction (rebase-era rewrite).** Starting from a clean `20ba1c9`:

1. Appended a marker to **120 result payloads** under `results/` — the files
   `RESULTS.md` cites as evidence. 120 files, provenance destroyed.
2. Committed. New HEAD `d559168`.
3. Ran the suite.

```
Ran 6 tests in 0.127s
OK
```

The seal's `generated_at` still reads `2026-10-01T04:14:56` — the old commit's clock —
while the tree it attests to is now `d559168`. **A seal that describes a tree which no
longer exists, and the guard says OK.**

Three further constructions, all green:

| # | what I did | guard |
|---|---|---|
| 1 | rewrote 120 `results/*.json` payloads the ledger cites | **6/6 OK** |
| 2 | squashed the last 3 commits, re-sealed | **6/6 OK**; only `generated_at` + content digests changed, no field names the new commit |
| 3 | hand-forged `generated_at` to `1970-01-01` | **6/6 OK** |
| 4 | hand-forged `generated_at` to `2099-12-31`, plus `schema` and the `doctrine` string itself | **6/6 OK** |
| 5 | injected a `sealed_from_dirty_tree` admission row by hand, without ever running `--allow-dirty` | **6/6 OK** |

### Why: 86% of the tree is outside the seal

```
tracked files        : 1237
sealed paths         :  166
UNSEALED tracked     : 1071  (86%)
```

The glob is `EXPERIMENTS.glob("*.py")` — **non-recursive**. It seals 145 top-level
`experiments/*.py` and misses the 645 tracked files beneath `experiments/`, including
`experiments/autoclaw-exp0830-run1/{train,prepare}.py`, which are experiment code. And
`receipts/` itself — *the receipt layer* — is unsealed, as is `tests/test_receipts.py`
(the guard does not guard itself) and `README.md` (which two tests assert against).

So the loop closes on the four paths it watches and is silent on everything else. The
docstring's promise — *"a result the ledger cannot re-derive is a claim, not a receipt"* —
holds for the ledger's own text and not for the evidence the ledger cites.

### The `--allow-dirty` hatch still reproduces

Unchanged from last round, re-verified at the new HEAD:

1. In-flight edit to `RESULTS.md`, uncommitted.
2. `python tools/receipt_manifest.py` → **REFUSED, exit 2.** The guard works.
3. `--allow-dirty` → seals the dirty bytes, records `sealed_from_dirty_tree: {admission: true, paths: [' M RESULTS.md']}`.
4. Commit that same edit.
5. **`Ran 6 tests ... OK`.**

And `test_receipts.py` never reads `sealed_from_dirty_tree` — it compares only
`ledgers`, `experiments`, `tools`. The admission is a certificate nobody audits.

### And the documented run executes zero tests

```
python3 -m unittest discover           ->  Ran 0 tests in 0.000s   OK    exit=0
python3 -m unittest discover -s tests  ->  Ran 6 tests in 0.132s   OK    exit=0
```

`tests/` has no `__init__.py`, so the bare `discover` collects nothing — **and prints
`OK` with exit 0.** The correct command is in the file's own docstring line 6
(`discover -s tests -v`), but the failure mode of getting it wrong is a green.

**Verdict: the pin is correct and the seal is not sound.** The guard is a content check on
4 of 21 top-level directories, with no git identity and an unaudited escape hatch, and
nothing runs it — there is still no `.github/` in this repo at all.

---

## 3. `fleetset` — DOES NOT EXIST

I was looking for the wrong thing, and I should have searched before reporting
`COULD-NOT-RUN` last round.

```
$ python3 -c "...scan fleet_meta.json (5,092 repos)..."
'fleetset'     -> []
'fleet-set'    -> []
'fleet_set'    -> []

$ for n in fleetset fleet-set fleet_set fleetset-tools superinstance-fleetset fleetkit \
           fleet-set-builder; do git ls-remote .../SuperInstance/$n.git; done
all 7 -> no
```

No repo in the 5,092 live repos has `set` in its name and `fleet` in its name. No
description mentions it. **`fleetset` is not private, not renamed, and not a typo I can
resolve — it does not exist.**

**The nearest thing that does: `fleet-kit`** (`5ad1e810`, Python, 200 KB) — *"Modular
toolkit extracted from Oracle1 fleet workspace — PLATO client, consensus, model router,
crab shell, audit tools."* It is the fleet's shared toolkit and the home of `fleetlint`.
That is almost certainly the repo the name referred to, but **I am inferring, not
confirming** — you may have been thinking of a repo that was never pushed.

---

## 4. The deliverable: `exectest.py`

`playtest2/exectest.py`. Stdlib only, no network. Three signals, cheapest first.

```
python3 exectest.py <repo> [--mutate] [--json]
python3 exectest.py --selftest
```

| signal | cost | catches | verdict power |
|---|---|---|---|
| **1 · IMPORT** | ms, static | the `voxelglyph` species — README's lead product module never imported | can fail a repo |
| **2 · LITERAL-ONLY** | ms, AST | `test_weights_sum_256` — assertions over literals and self-bound locals, no product name read | evidence only, never fails a repo |
| **3 · MUTATION** | minutes, mutates a **copy** | everything, including the unfailable-judge species | the only signal that can fail a repo alone |

**Signal 3 copies the repo to a tempdir, mutates there, and restores between mutations.**
The caller's tree is never written to. If a mutation *should* have been caught and wasn't,
the exit code is 1 and the tool says so.

### The negative control

The brief required: flag `voxelglyph`'s pre-fix state, stay silent on `pong-quilt`.

```
voxelglyph-PREFIX (must FLAG) ... PASS  verdict=VACUOUS
pong-quilt (must NOT flag)    ... PASS  verdict=EXECUTES-PRODUCT
```

**And I have to report that the control failed four times before it passed.** It is part
of the result, not a confession of sloppiness — every failure was the tool over-firing,
and the brief said a tool that flags everything is broken and must be reported as such:

1. **`pong-quilt` flagged VACUOUS.** My JS import scan only understood `import ... from`.
   `pong-quilt` uses CommonJS `require()` and `fs.readFileSync` of the product source.
   Both are legitimate product references; neither was counted. → added both patterns.
2. **`pong-quilt` then ALREADY-RED.** `node --test tests` treats the directory as one
   unit; the suite needs `node tools/build-site.mjs` first because tests byte-pin
   `site/dist` against source. → runner now runs `npm run build` when a build script exists.
3. **`voxelglyph-prefix` COULD-NOT-RUN.** I used `discover -s tests -t .`, which requires
   `tests/__init__.py`; this repo has none. → runner now tries several invocations and
   keeps the one that *collected the most tests*, because `unittest discover` prints `OK`
   on zero.
4. **`voxelglyph-prefix` came back EXECUTES-PRODUCT.** It *does* import `syzygy_port` — a
   helper. "Imports a product module" was too weak a question. → signal 1 now asks whether
   the **README's first-named product module** is imported. It isn't; the suite imports a
   port and verifies a copy of the arithmetic.

Then the over-fires on *other people's repos*, which I found by reading the tool's output
against the source rather than trusting it:

- **`fleet-kit` 18 → 0 false positives.** Three separate causes, each a real blind spot I
  had not thought of: (a) `result = self.auditor.audit(...)` binds a local from the
  product, so a fixpoint taint pass is needed; (b) the product is sometimes called as a
  bare *statement* (`crab.register()`) with nothing bound at all; (c) `fleet-kit` loads
  its product with `importlib.util.spec_from_file_location` + `exec_module`, so the
  product class `PlatoClient` never appears in an `import` statement.
- **`quilt-canary-port` flagged VACUOUS.** The suite does `from quilt_canary_port.python_port
  import ...` and the README says `quilt_canary_port/python_port.py`. My normaliser
  stripped extensions inconsistently from the two sides.
- **`micrograd-quilt` flagged VACUOUS.** The suite does `from quilt import auditor`; the
  README says `quilt/auditor.py`. I was expanding dotted-path suffixes on the import side
  but not on the README side, so every package/module pair looked like a miss.
- **`cell-doctrine` was missed entirely** (a `test.js` at the repo root doesn't match
  `test_*.py` or `*.test.js`). A detector that under-counts is as wrong as one that
  over-fires. → added bare-name suite detection.

Each of these was found by me reading the flagged repo and finding the tool wrong. **None
of the four repos' code was changed to make the tool pass.**

### What signal 3 actually found in the fleet

**13 repos where every mutation survived.** The `substrate-*` family is a single defect
repeated ten times, and it is the purest specimen of anything in this report:

```js
// substrate-witness-log/test.js  — the ENTIRE suite, 7 lines
try {
  const result = require('./index.js');
  console.log('OK: ' + Object.keys(result).join(', '));
} catch (e) {
  console.error('FAIL:', e.message);
}
```

Proof: I replaced the product's `return entry;` with `return null;` and ran the suite.

```
FAIL: Cannot find module '@superinstance/observation-primitive'
EXIT CODE = 0
```

**The product is destroyed, the suite prints the word `FAIL:`, and the exit code is 0.**
Any CI, any `&&` chain, any `cron` reading exit status sees green. Ten repos —
`substrate-bundle`, `-canary-pin`, `-contest`, `-delegate`, `-membership`, `-merger`,
`-revoke`, `-traverse`, `-withdraw`, `-witness-log` — are 6–7 line smoke tests over
25–76 line products, and **not one has a `.github/` directory.** There is no mechanism by
which these have ever been executed by anything.

`substrate-attest` is the eleventh and is different: its `test.js` has **zero
assertions** — it constructs three attestations and `console.log`s them. It scores
`ALREADY-RED` because it `require`s an unpublished package, so it has never run anywhere.

`quilt-cell` is the honest partial: 1/3 caught. Its suite really does import the product
and assert behaviour, but inverting a clamp —
`const nRefsQ = Math.min(0x7FFF, nRefs * 256)` → `Math.max(0x7FFF, nRefs * 256)` —
leaves it printing `✓ all checks passed`. **A real suite with a real hole in it**, which
is the most useful kind of finding.

---

## 5. What stopped me, and where this number should not be trusted

**The 275 repos are not a random sample.** They are whatever a prior scouting pass
decided to clone. `fleet_meta.json` says 5,092 live repos. I examined 5.4% of the fleet
and it happens to be the 5.4% that looked interesting enough to clone, which is a
selection effect I cannot undo. **Treat "8 of 275" as a rate measured on a biased sample,
not as a fleet-wide count.** The unbiased number is: I could check 275, and here is what
they said.

**The 202 NO-SUITE verdicts are the load-bearing limitation.** 73% of the sample has no
file matching test conventions. I spot-checked four (`circuit-breaker-rs`, `cocapn-abyss`
— genuinely none) and found one the tool had missed (`cell-doctrine`), which I then fixed.
But most are Rust/Go/Julia/docs repos I never had the toolchain to run. **"No suite" here
means "no suite in the conventions my tool knows," which is weaker than "no tests."**

**ALREADY-RED is 26 repos and I did not adjudicate them.** A red suite is not a vacuous
one; some of those 26 are simply broken. I report the count, not a verdict.

**Two known tool limitations, stated because they change numbers:**

- `fleet-static-host` scored 0/2, but that is **my tool choosing the wrong file** — it
  mutated `build_site.py`, a build script, instead of the `.ts` the suite actually tests.
  When I ran the documented `npm test` by hand the suite runs 18 tests green. **Its 0/2 is
  a tool artifact and should be struck from the 13.**
- `opcode-canon` and `quilt-canary-port` were skipped — no mechanical mutation candidate
  in the file the tool selected. `quilt-canary-port` I checked by hand: it ships four
  ports (python/rust/javascript/sql) and its 4 tests import exactly one. **The other
  three are untested**, which is a real gap the tool could not express.

**The mutation signal is shallow by construction.** It offers up to six mechanical
candidates — first `return` made falsy, first `*` zeroed, `max`↔`min` — and does not
choose well. `pong-quilt`, the fleet's best-tested repo, got one candidate and it was
caught. A repo can pass signal 3 by being lucky.

---

## 6. What I would tell the orchestrator

1. **`quilt-tools`' defect is one line, not a design flaw.** `budget-tide.mjs:112` ends in
   `|| true`. It is unfailable in the committed tree, no mutation required. But the 94
   checks are overwhelmingly *semantic* — CUSUM change-point positions, hysteresis flip
   counts, honest absences. Your format-check hypothesis does not survive contact with
   them. The real gap is that `check()` has no test and CI runs 1 of 11 tools.

2. **The seal question has a demonstrated answer, and it is the bad one.** I built the
   stale-manifest case you hoped I couldn't: rewrite 120 result payloads the ledger cites,
   commit, re-seal, and the guard is 6/6 green while `generated_at` still reads the old
   commit's clock. 86% of the tree is outside the seal; the glob is non-recursive; the
   manifest binds no git identity; the dirty-seal admission is unaudited. And
   `unittest discover` prints `OK` on zero tests.

3. **`fleetset` does not exist.** Not private, not renamed — absent from 5,092 repos and
   from seven `git ls-remote` probes. The nearest real repo is `fleet-kit`, but that is
   my inference and you should confirm what you meant.

4. **The number: 8 of 275, on a sample I did not choose.** The more actionable figure is
   the survivor rate — **13 of 22 repos where mutation was possible let the product break
   silently**, and 11 of those 13 are one fail-open `try/catch` in a 6-line file, ten of
   them in the `substrate-*` family, none with CI. That is a copy-paste family, and it is
   fixable by one rule: *a test harness must exit non-zero on failure.* `exectest.py`
   flags all of them.

5. **The tool's own negative control failed four times before it passed**, each time by
   over-firing, and I found every remaining false positive by reading the flagged repo
   rather than trusting the output. That is the honest characterisation of a static
   detector at this stage: **it is a prompt for a human, not a verdict.** The mutation
   signal is the only part I would let fail a repo unattended, and even it is shallow.

**Nothing was fixed. No commits, no pushes. All five checkouts at their original HEADs;
the four constructed failure states were made in copies and deleted.**
