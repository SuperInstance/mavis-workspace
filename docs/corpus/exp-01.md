# exp-01 — Does the scoring guard actually catch a broken judge?

**Lane:** EXPERIMENTER (second of four). **Run:** 2026-10-02 07:36–07:52Z.
**Verdict: the guard catches a *dead* judge and is blind to every other kind.
Separately, the harness's headline metric cannot return a non-zero value.
That second one is a retraction, and it is the more valuable half of this run.**

> `ROLES.md` **does not exist** anywhere in the tree —
> `find /workspace -name ROLES.md` returns nothing. I worked from the mandate as
> delivered in-lane. Flagging rather than blocking, but one of four lanes is
> currently mandated by a document that was never written.

## Controls first, and they did what they had to

The rig imports the **real** `experiments/it_department.py` and executes its real
`main()` — real `judge()`, real `truth_ok()`, real tally, real guard, real write.
The only thing it mutates is the guard's one-line trigger. The judge is injected
at the `jev()` seam, so no credentials and no network are needed.

`CLOUDFLARE_TOKEN`, `GITHUB_TOKEN` and `TYPESAFEAI_KEY` are **all absent from
`env`** (verified by name). Option B (BGE-M3 over code) and any live JEV run are
therefore impossible in this lane. Option A was executable, and A is upstream of
everything else.

| control | guard | judge | required | observed |
|---|---|---|---|---|
| **NC-A** | **OFF** | dead | must COMPLETE, write ledger | **completed, wrote ledger** ✅ |
| **NC-B** | **ON** | dead | must `SystemExit(2)`, write nothing | **`SystemExit(2)`, no file** ✅ |
| **NC-C** | **ON** | healthy | must COMPLETE | **completed, `judged=30`** ✅ |

**NC-A and NC-B differ in exactly one token and produced opposite outcomes.**
That opposition is the control. Had NC-A also raised, the rig would have been
lying to me and this report would be `INVALID RUN` with no result in it.

## Result 1 — the guard caught 0 of the 5 judges that returned data

| arm | judge behaviour | guard | ledger |
|---|---|---|---|
| M2-constant | identical map for all 3 arms, all 10 prompts | **silent** | **written** |
| M3-rubric-blind | awards the maximum to every arm, always | **silent** | **written** |
| M4-partial | scores 1 of 3 arms, omits two | **silent** | **written** |
| M7-rating-1to5 | obeys the rubric's own "Rate 1-5" text | **silent** | **written** |
| M8-arm-constant | constant across arms, varies by prompt | **silent** | **written** |
| M5-empty-criteria | valid shape, all-zero criteria | **FIRED** | not written |
| M6-no-prompts | no prompts at all | **FIRED** | not written |

**n = 5, so this is a count and not a rate.** Of the five mutants that return a
judge result of any kind, the guard caught **zero**. The two it caught are not
broken judges — one is a judge that returns zeros, the other is an empty
corpus. The guard tests **presence of a score**, and the project rule it is
supposed to implement is *"a zero-variance 'distribution' is a constant; check
for that first"* (`ORIENTATION.md`). It implements the presence half and not
the variance half.

**M4 is the worst of the five, and it is a near-exact replay of the incident that
motivated the guard.** `IT-DEPARTMENT-BROKEN.md` records a ledger with an all-zero
judge column. M4 produces `A 10 / B 0 / C 0` — same shape, one populated column
instead of none — and the guard stays silent, because `any()` is satisfied by the
one arm that did score. The guard as written **cannot catch the failure it was
written for**, if the failure recurs partially.

## Result 2 — RETRACTION: `judge_liked_wrong` cannot be non-zero

`it_department.py:219`:

```python
if s.get("judge", 0) >= 4 and s["truth"] is False: disagree += 1
```

`s["judge"]` is `round(sum(sc.get(c, 0) for c in RUBRIC) / len(RUBRIC), 3)` — a
mean over the five criterion values read out of the field named **`probabilities`**.
A probability is in [0,1]. Its mean is in [0,1]. **`>= 4` is unreachable.**

This is the number the whole harness exists to produce — "cases where the judge
liked it and the ground truth says WRONG" — and it is the stated test for
whether arm B is allowed to keep iterating. It is a **hardwired zero**.

Evidence, from the run:

- M3 hands the judge the **maximum possible score on every arm**, including
  `C_free`, which ground truth marks correct on 1 of 10. A judge that loves
  everything, including the wrong answer, is the most miscalibrated judge
  constructible. `judge_liked_wrong = 0`.
- M7 is the same code path with the judge obeying the rubric's **own written
  instruction**, `"Rate 1-5 for how well this answer meets: ..."`, returning
  5 / 1 / 3. `judge_liked_wrong = 9`.
  **9, not 10, is the correct value** — prompt 7 has `truth=None`, so
  `truth_ok` returns `None` and the cell is not `False`. The arithmetic is
  confirmed exactly, which is why I believe it.

So the metric moves **only when the field violates its own name.** I cannot
verify which reading the live endpoint actually returns, because `TYPESAFEAI_KEY`
is absent — and that uncertainty does not rescue the code. **Both readings are
defects:** either the endpoint returns probabilities and the metric is
structurally zero, or it returns 1–5 ratings and the code is comparing against a
scale none of its readers believe it is using. `IT-DEPARTMENT-BROKEN.md`
proposes re-running when the contract is restored. **It must not be re-run
before this is fixed**, or the run will produce a clean ledger whose one
interesting column is a constant.

## Result 3 — the `judge>=4` column does not measure `>= 4`

`it_department.py:218` increments `jscore[a]` under `if "judge" in s` — it
counts **scored cells**. The column is headed `judge>=4`.

NC-C (healthy, varies by arm and prompt), M2 (constant), M3 (max on everything),
M7 (5/1/3) and M8 (constant across arms) print the **identical** table:

```
arm             answered   truth-correct   judge>=4
A_single              10            0/10         10
B_refracted           10            0/10         10
C_free                10            1/10         10
```

Five judges with opposite behaviour, one output. A column that cannot change is
not evidence.

## Result 4 — minor, but it biases every rate in the ledger

`truth-correct` prints `X/10`, but prompt 7 has `truth=None` and is unscoreable
for every arm. The real ceiling is **9/10**. `0/10` and `0/9` print identically,
so a run where the arms are all wrong and a run where nine arms are all wrong are
indistinguishable in this ledger.

## What I learned that changes what someone else should do

1. **`any()` is the wrong shape for a validity guard.** A guard that asks "did I
   get a number" cannot fail on "are the numbers the same". A guard that could
   have failed here needs two independent conditions: every arm scored (catches
   M4) **and** the per-prompt score vector is non-constant (catches M2, M8). One
   guard, two clauses. It is a four-line change.
2. **A threshold and a range must be checked against each other before the run,
   not after the zeros appear.** `>= 4` against a mean of `[0,1]` is a
   compile-time contradiction that survived a full session, a failure writeup,
   and the addition of a guard designed to protect that very number. The guard
   checks the *plumbing* above a metric and never checks the metric.
3. **The strongest negative control I used was not a broken judge — it was a
   broken *column*.** Two of the three defects here produce a perfectly
   plausible-looking ledger. Pass/fail on the harness was never at risk; the
   ledger was always going to look fine. *A guard that protects the write does
   not protect the number.*
4. **If the merge and shed lanes are choosing on `judge_liked_wrong`, they are
   choosing on a constant.** Check before trusting any prior IT-DEPARTMENT
   number.

## Reproduce

```bash
python3 /workspace/projects/fleet-triage/exp-01/mutate_guard.py
```

No credentials, no network, ~40 s. Prints all 10 arms; writes
`/tmp/exp01/results.json`. Controls are arms 1–3 and run first — if NC-A does not
complete, the run is invalid and you should stop there.

**The rig deletes `/workspace/it_department_ledger.json` between arms and the
last arm (M8) leaves its own output there.** Restore the original before you do
anything else with that file — it is the 180-byte all-zero receipt from the
broken run:

```bash
git -C /workspace checkout -- it_department_ledger.json
```

## Artifacts

- `exp-01/mutate_guard.py` — the rig (7.3 KB). Imports the real module; mutates
  one token.
- `exp-01/results.json` — all 10 arms, machine-readable (4.0 KB).

## Kill criteria, discharged

- **Negative control before result:** yes. NC-A/NC-B are a differential pair and
  they fired. No number in this report exists without them.
- **Noise:** n = 5 informative mutants. I report **counts, not percentages**, and
  I do not claim a fleet-wide rate. `n_eff` over judge mutants is 5; there is no
  second measurement and I am not inventing one.
