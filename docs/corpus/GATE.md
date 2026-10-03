# GATE.md — one gate, four discriminators

**Status: all four rules live, 15/15 constructed controls green, run over 49
priority repos.** The stub (rules 1–2 + controls) landed at T+35min against a
10-minute target; the overrun is mine and the reason is at the bottom.

```bash
cd /workspace/projects/fleetlint
python3 -m fleetgate controls                    # 15 constructed controls
python3 -m fleetgate run                  <repo>  # all four rules, gated
python3 -m fleetgate records-a-failure   <repo>  # one rule
python3 -m fleetgate explain             [rule]  # why it exists
```

Standard library only, no install, no model call, no network. If a rule costs a
model call to run it will not be run, and an instrument that is not run is the
subject of this fleet's entire problem.

**The finding underneath all four:** the load-bearing element is always the
boring one — the enumerator, the provenance, the record of the red, the metric
whose denominator exists — and the expensive impressive thing is decoration.

**Three verdicts, not two.** `fail` / `ok` / `unknown`. `unknown` is not a softer
`ok`. A gate that passes what it did not measure is the `echo "No CI configured"`
placeholder with better branding.

---

## Bottom line first

| # | finding | verdict |
|---|---|---|
| 1 | `durable-LOGIC` — the canary split, 3/4 | **REPRODUCED.** 10/10 on the named set, plus the `got = expected` defeat probe confirmed with a two-sided control. |
| 2 | `r3-SWAP` — the seam boundary, composed apps | **NOT REPRODUCED. Not testable as stated.** The rule works on constructed controls and fires on 9 real repos, but I have no labelled corpus of enumerated vs composed apps, so I cannot score it. This is the one of the four still believed for free. |
| 3 | `r3-JEVPATTERN` — the metric precondition | **PARTIALLY REPRODUCED.** The rule is right on the reference defect and found the same shape live in the fleet. But its acceptance test — "catch all three of my failed experiment metrics" — **is not achievable**, and §Rule 3 says why. |
| 4 | `res-CLUSTER` — provenance beat the embedding | **THE DISCIPLINE IS NOW CHECKABLE; the result is not re-verified.** The rule found one real instance. Whether provenance is *faster* is not something a linter can measure. |

**How many of the four did the gate catch: 2 fully, 1 partially, 1 not at all.**

---

## Rule 1 — `records-a-failure`

**Discriminator.** A check whose only committed evidence is a green result cannot
be told apart from a check that does not run. The load-bearing element is not
the passing; it is a committed record of the check having gone red.

**Why it is not a filename match.** The signal is *content* — a committed
artifact containing a **verdict line**. A rule keyed on the literal word
`failfirst` would pass these seven repos and prove nothing, because these seven
are the only seven in the corpus containing that word.

### Controls

| control | want | got |
|---|---|---|
| `r1_green_only` — suite + CI + a **green** receipt + a README that talks about failing constantly | `fail` | `fail` |
| `r1_with_red` — the *same repo, same prose*, plus one observed red in `evidence/2026-09-30-run.txt` | `ok` | `ok` |
| `r1_no_apparatus` — prose, nothing that runs | `unknown` | `unknown` |

The red record in `r1_with_red` lives in a file whose name has nothing to do with
the answer. A rule matching names would pass it for the wrong reason, which is
why the corpus — not the control — is where that class of rule is caught.

### Two defects the corpus found in my own rule before it found anything in yours

**1. `0 checks fail` inside a green summary.** The first pattern matched the
word `fail` anywhere, so `SUMMARY: 3/3 checks pass (3 checks pass, 0 checks fail)`
counted as a record of the red. It accepted every honest green receipt in the
fleet. Fixed: counts must be non-zero, and green zero-count clauses are stripped
before matching.

**2. Prose about failure is not a record of failure.** This one mattered. Over the
real corpus the word-list version returned **`ok` for `moth-ledger` and
`moth-corpus`** on the strength of these sentences:

```
A hunt that failed is data, never noise.
ok, errors = ledger.verify_chain()
fails loud, not silently stale
| `REFUSAL/v1` | hunt failure: budget exhausted, tool refused, cap hit |
```

A rule that cannot tell a description of a red from a red is not a
record-of-failure check; it is a grep, and it had quietly become the defect it
was written to catch. The fix is a **line-anchored verdict grammar** — a non-pass
verdict at the head or the tail of a line, a non-zero fail tally, a `k/n pass`
ratio with `k < n`, or a structured verdict field. Every alternative is anchored,
so a sentence containing the word cannot match.

Both of those prose shapes are now **in the control**. The control got harder.

### Result on the seven repos in the finding

| repo | verdict | committed red |
|---|---|---|
| `moth-ledger` | **fail** | none |
| `moth-corpus` | **fail** | none |
| `moth-cells` | **fail** | none |
| `moth-honest` | **fail** | none |
| `quilt-in-git` | ok | `pins/failfirst*.log` (7 files) |
| `frozen-clock-lab` | ok | `pins/failfirst.log` — `FAIL-first: lab/ absent` |
| `doubt-ledger` | ok | `pins/failfirst*.log`, `pins/guardian-failfirst.log` |

**7/7.** The rule identified `moth-*` without being fitted to it.

### The defeat probe: `got = expected`

The finding's second claim is that `moth-honest` is *uniquely* the canary that
survives having its comparison replaced. That is a runtime claim, so I ran it,
both directions, on `moth-honest/src/moth_honest/vendor_hashes.py:40`:

```python
got = fnv1a_64(raw)
if got != expected:
    raise AssertionError(f"bytes-law pin broken: {raw[:24]!r}")
```

| taint | result | meaning |
|---|---|---|
| **A** — insert `got = expected` above the check, so the measurement is overwritten by its own expectation | **33 passed, exit 0** | the canary does not notice |
| **B** (control) — flip one bit of a value in `PINNED_VECTORS`, leaving the check itself real | **2 FAILED, exit 1** | the check *does* fire when the check is real |

**Confirmed, and this is the sharper test than the one in the finding.** TAINT B
is the ordinary mutation: it proves the suite *touches* the code. TAINT A is the
inverse — make the implementation trivially correct and see if anything notices.
Nothing noticed. The suite constrains the *expected value*; nothing constrains
the *measurement*. Two taints differing only in which side is corrupted, one
caught and one not.

This is the same disease as the `quilt-llvm` table already in the fleet's
memory — 1,127 input-level semantic mutants killed at 0.0% against a tamper
control firing 76/76. Second independent instance, and the two repos do not share
code.

### What rule 1 flags across the priority set (49 repos)

`fail` 24 · `ok` 6 · `unknown` 19

- **7/8 `moth-*` fail** (`moth-jev-adapters` is `unknown` — it commits no
  verification apparatus at all, which is a different and worse thing).
- **3/3 keepers pass**, each on a real `failfirst` log.
- **17/30 `substrate-*` fail.** The canary split is not a `moth-*` property; it
  is the fleet's default posture, and `moth-*` is where you happened to look.

---

## Rule 2 — `enumerates-from-own-state`

**The seam in one line.** If the enumeration takes anything the app did not
derive from its own state, the app is composed, and it will need a chooser to
exist.

**Why static.** A behavioural test needs a chooser to exist in order to observe a
seam, so a composed app is invisible to any test that runs it happily. Static
provenance of the iterable is the only thing available before the chooser is
written. Python goes through the real `ast`; every other language gets a
conservative line scanner and reports `unknown` rather than guessing.

| control | want | got |
|---|---|---|
| `r2_enumerated_literal` — moves are a tuple literal | `ok` | `ok` |
| `r2_enumerated_own_state` — moves derived from `self` | `ok` | `ok` |
| `r2_composed_imported` — `from some_other_package.prior import MOVE_TABLE` | `fail` | `fail` |
| `r2_composed_fetched` — `for x in suggestions(state)` over `urlopen(x).read()` | `fail` | `fail` |
| `r2_composed_model` — `for c in client.chat.completions.create(...)` | `fail` | `fail` |

### This is the rule I could not score

`fail` 9 · `unknown` 40 · `ok` 0 over 49 repos.

**40 of 49 are `unknown`.** The rule is a correct discriminator on five
constructed cases and it fires on 9 real repos — `moth-ledger` (21 sites),
`substrate-walker` (17), `moth-honest` (7) — but I have **no labelled corpus of
enumerated vs composed apps**. Every one of those 9 is a hypothesis, not a
detection. I did not check a single one by hand, so I cannot tell you how many
are real.

**Rule 2 is the one of the four that is still believed for free.** It is also
the rule the finding claims is "one line of static analysis", and the one-line
statement is about the *criterion*; turning it into a check took a real parser, a
one-level intra-module return-value resolver, and a dotted-name foreign-call
table, and it still resolves free names in only about a fifth of the sites it
sees. The honest statement is: **the criterion is one line and the checker is
not.**

---

## Rule 3 — `metric-is-defined`

> The disease is not a wrong sign or a wrong winner; it is a metric whose
> denominator contains positions where the numerator does not exist.

| control | want | got |
|---|---|---|
| `r3_guarded_over_total` — the reference defect, reconstructed from `experiments/synergy.py` | `fail` | `fail` |
| `r3_same_population` — the same metric repaired | `ok` | `ok` |
| `r3_loop_mismatch` — `hits/seen` where only `hits` is guarded | `fail` | `fail` |
| `r3_plain_mean` — `sum(xs)/len(xs)`, unguarded | `fail` | `fail` |

The reference control is a *perfect instrument that must return 1.0 and returns
the base rate*, which is the shape of `detection_power`.

### It found the reference defect, live

`substrate-walker/playtest/jev_lore_gen.py:117`

```python
avg = sum(e["jev_scores"][v]["canon"] for e in out if v in e["jev_scores"]) / len(out)
```

The numerator reads a subscript that does not exist on every row; the divisor
counts every row. A perfect canon score returns the *base rate*. This is
`detection_power` again, in a different repo, written by nobody who was looking
for it. That is the strongest single piece of evidence in this report and it was
not in any brief.

### The acceptance test is mis-specified, and I am not going to pretend otherwise

The brief says this rule "should have caught all three of my failed experiment
metrics". The three errors in `EXPERIMENTS.md` are:

1. **`detection_power` divided by the wrong denominator.** → a definedness
   failure. **This rule catches it.**
2. **Published the max of four learners per condition** (`n_eff = 1.48`, ordering
   reverses under the median). → a *selection* failure. The metric is perfectly
   defined at every position; the thing that is wrong is which sample was
   reported.
3. **Used a random 80/20 split instead of the by-ply split**, so L4 tied the
   lossless board. → a *leakage* failure. The metric is defined on the population
   it was measured on; that population is not the population it was reported
   about.

Only one of the three is "a metric whose denominator contains positions where
the numerator does not exist". Number 2 needs a `no-selection-before-report`
rule (a reported figure that is a `max`/`best`/argmax over a set, with no
dispersion figure beside it). Number 3 needs a `split-is-not-leaking` rule. Both
are worth writing and neither is this rule. I would rather say that than widen
`metric-is-defined` until it nominally catches three things it does not
understand.

### A false-positive class I am reporting rather than tuning away

Rule 3 also flags **predicate rates**:

```python
horizon_active = sum(1 for d in horizon_band if d > 0.2) / len(horizon_band)
```

"Fraction of the population above 0.2" is a legitimate rate over the whole
population — the numerator is 0, not absent, at every position below the
threshold. It is structurally identical to `detection_power`'s guard (`count of
rows where t == 1, over all rows`) and **static analysis cannot separate them
without domain knowledge.** I could suppress this class until the counterexample
disappears, and that is exactly how a rule gets fitted to an answer, so I left it
standing and counted it. Expect roughly one predicate-rate finding per repo that
computes a threshold rate. There is no `--allow-predicate-rate` switch, because a
switch that nobody counts is a switch that makes the number mean whatever the
reader wants.

### Coverage

`fail` 1 repo · `ok` 1 · `unknown` 47. Rule 3 only evaluates Python and only one
repo in the set had a division site it could see.

---

## Rule 4 — `provenance-before-embedding`

| control | want | got |
|---|---|---|
| `r4_provenance_first` — grouped by `repo_full_name`, embedding is a nicety | `ok` | `ok` |
| `r4_provenance_unused` — `cos(a,b) > 0.82` decides, `repo_full_name` unused | `fail` | `fail` |
| `r4_provenance_absent` — nearest-neighbour, no exact key anywhere to compare | `unknown` | `unknown` |

### One real instance

`substrate-walker/canon/auto_filer.py:4,38,40`

```
discovered (score >= 0.86), it gets a canon cell file with FNV-1a hash.
if score >= 0.867:
```

Three similarity thresholds decide duplication, twenty-three lines in the same
file name an exact provenance key, and the file computes an **FNV-1a hash** —
the exact function, the boring one — without using it to decide or break the
tie. That is the `res-CLUSTER` shape, and it is a threshold somebody has to
argue about on every run, sitting next to a hash that answers the question.

### What this rule does not establish

`res-CLUSTER`'s claim is that provenance answered the question **faster and
exactly**. The rule checks the *shape* — an embedding deciding where an exact
key exists and is unused. It cannot measure the speed, and it does not confirm
the original comparison was run. The discipline is now checkable; the result is
taken on trust.

`fail` 1 repo · `ok` 21 · `unknown` 27 over 49.

---

## The numbers, including the ones nobody reports

| rule | fail | ok | unknown | informative rate |
|---|---|---|---|---|
| `records-a-failure` | 24 | 6 | 19 | **59%** |
| `enumerates-from-own-state` | 9 | 0 | 40 | **18%** |
| `metric-is-defined` | 1 | 1 | 47 | **4%** |
| `provenance-before-embedding` | 1 | 21 | 27 | **45%** |

**Informative rate** = (fail + ok) / total. The rest is the rule declining to
answer, which is the honest floor and the one number worth watching as the rules
improve.

### False negatives: the number nobody reports

- **36 of 49 repos have no Python at all.** Rules 2 and 3 are effectively
  Python-only; the fleet is `.ts` (272 files), `.js` (146), `.rs` (47). Over
  those 36 repos rules 2 and 3 return `unknown` and **rule 2 has never once been
  exercised on a real composed app in TypeScript, which is where composed apps
  are actually written.**
- **Rule 1's `ok` class is contaminated.** 3 of the 6 passes
  (`substrate-embedding`, `substrate-rng`, `substrate-llm-client`) got their
  green verdict from a **`README.md` / `LEGIBILITY.md`**, not a run log. A README
  quoting a failure is closer to prose than to an observation. Those three
  should be `unknown`, not `ok`. The verdict grammar is right at the line level
  and wrong at the *artifact* level: it has no notion of "this file records a
  run" versus "this file describes one".
- **Rule 2 has 0 `ok` verdicts in 49 repos.** A rule that never confirms anything
  is not yet discriminating; it is only accusing.
- **Rule 1 cannot see `.github/workflows` output** unless it is committed, so a
  repo whose only red ever existed in CI is scored the same as a repo that never
  went red.
- **Nothing here is a mutation test.** Every one of these rules reads committed
  text. They can all be defeated by rewriting the artefact, and the only rule
  with a demonstrated defeat resistance is rule 1's *runtime half*, because that
  one actually executes.

### What the gate found that was not in the brief

- **17/30 `substrate-*` commit only green evidence.** The canary split is the
  fleet's default posture, not a `moth-*` quirk.
- **`substrate-walker/playtest/jev_lore_gen.py:117` is `detection_power` again**,
  live, in a repo nobody was auditing.
- **`substrate-walker/canon/auto_filer.py` decides on three similarity
  thresholds next to an unused FNV-1a hash.**
- **`moth-jev-adapters` commits no verification apparatus whatsoever** — not a
  green badge, not a test. Rule 1 scores it `unknown` and that is the correct
  answer, but it means the finding's "4 of 7" is really "7 of 7 that have
  apparatus, and one that has none".
- **Two of the four findings were only checkable because the corpus caught bugs
  in my own rules first.** Both rule-1 defects were found by running against
  real repos, not by the controls. The controls caught a filename rule; the
  corpus caught a vocabulary rule.

---

## Why the stub took 35 minutes

The 10-minute target assumed the two easy rules were two easy rules. Rule 1 took
three attempts: the word list, the line-anchored grammar, then the green-clause
strip. Rule 2 needed a real parser, a return-value resolver and a dotted-name
table, and `_dotted` had to learn to see through a call on a call
(`urlopen(x).read()`) before the fetch control stopped falling through to
`unknown`. The 15 controls are not decoration either — **they were wrong five
times**, and every one of those five was a rule defect, not a bad expectation.
I could have shipped at 10 minutes with 8 controls and a rule that accepted
`moth-ledger` on the sentence "A hunt that failed is data". That is the trade I
declined.

## What I would do next, in order

1. **Write `no-selection-before-report` and `split-is-not-leaking`.** Two of the
   three named experiment errors are not definedness failures, and both are
   checkable. That would make rule 3's stated acceptance test achievable instead
   of mis-specified.
2. **Give rule 1 an artifact-level test**, not just a line-level one: an
   observation is a log/tap/junit/runner file, or markdown under a path that
   denotes a run. Fixes the 3 contaminated `ok`s and probably surfaces more
   `fail`s.
3. **Port rule 2 to TypeScript.** 272 `.ts` files in a 49-repo sample and a
   Python parser is the coverage story of this whole report in one line.
4. **Get labels for rule 2.** Twenty hand-adjudicated repos, ten enumerated and
   ten composed, would convert the biggest `unknown` column into a number. Until
   then the seam claim is untested, and untested is not the same as true.
