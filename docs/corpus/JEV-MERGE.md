# JEV-MERGE — can the judgment oracle actually adjudicate a merge?

**Date:** 2026-10-01 21:34–22:55 UTC
**Question:** the competition entry's one untested assumption — that JEV (`jev-1.13.0`) can adjudicate a real merge conflict better than a line merge.
**Method:** real claims from the fleet, ground truth established by **executing the code**, never by asking the model.
**Calls:** 336 (round 1) + 252 (round 2) + 105 (confirmation) = **693 live calls, 0 transport/parse failures.**
**Artifacts:** `/tmp/jevm/{claims.json,results.json,results2.json,seedview.txt,analyze2.py}` — `/tmp` is ephemeral, re-runnable from the scripts in this file's footer.

---

## 0. The short answer

**No. On the specific claim that matters, JEV is confidently wrong, and it is wrong in the direction that makes the product unsafe.**

On the #32/#33 counter, asked *"is PR #32's count correct?"*, JEV answers **"correct" at p=0.97**. The count is wrong. The real merged number is **19 edges / 15 VERIFIED / 4 PENDING**, and I established that by running the code.

Worse, and this is the part that should stop the entry: **when handed both PR bodies and asked whether the real count is 19/15/4, JEV says "incorrect" — 5 times out of 5.** It adopts the disputants' numbers as ground truth and denies the only true one.

The entry does not need a different *adjudicator*. It needs a different *kind* of adjudicator, and §7 says which.

---

## 1. The fixture, and the ground truth I established myself

Your fixture is real, and I confirmed it independently.

```
SuperInstance/quilt-tools PR #32  closed, merged=true  2026-10-01T20:08:03Z  fb2e041
SuperInstance/quilt-tools PR #33  closed, merged=true  2026-10-01T20:29:03Z  0101409
SuperInstance/quilt-tools PR #34  open

$ git merge-base --is-ancestor fb2e041 origin/main   -> ON MAIN
$ git merge-base --is-ancestor 0101409 origin/main   -> ON MAIN
$ git diff origin/main...origin/pr/32                -> (empty)
$ git diff origin/main...origin/pr/33                -> (empty)
$ git diff origin/main...origin/pr/34                -> 3 files, +129/-17
```

Both merges are on main. The `#34` hazard is gone — `#34` branched on top of both
(`git merge-base origin/main origin/pr/34` = `0101409`), so there is no live invalid-syntax
merge to adjudicate. **The merge that needs adjudicating is historical.** That is a fact you
should weigh before spending more of the runway on it: the fixture no longer exists as an open
conflict, and #32/#33 are two commits in a log, not two live claims.

### The recount, executed

```js
const g = new ReferralGraph({ name: 'recount' });
for (const n of SEED.nodes) g.addNode(n);
for (const e of SEED.edges) g.book(e);
```

```
nodes        : 32
repos        : 17
TOTAL EDGES  : 19
VERIFIED     : 15
PENDING      : 4
```

**Your number is right: 19 / 15 / 4.** Independently confirmed. The steward's 21/17/4 is the
post-`#34` figure (19+2, 15+2) and is also correct for its own state. No correction needed.

### The actual collision — and it is nastier than "one of them is wrong"

| | asserted | true |
|---|---|---|
| PR #32 body | `18 edges: **14 VERIFIED · 4 PENDING**` | 19 / 15 / 4 |
| PR #33 body | `pins.mjs: 17→18 edges, 13→14 VERIFIED` | 19 / 15 / 4 |

**Both are wrong, and both are wrong by exactly +1 edge and +1 VERIFIED.** Each author counted
from a base that excluded the other. This is not "one author is right"; it is a **compositional**
conflict where the true state is the union and *neither party asserted it*. #33's base was
`fb2e041` — #32's merge — so #33 was rebased onto #32 while its prose still carried #32's
pre-merge numbers.

**This is the merge problem the competition entry is actually about, and it is the one case
where a judgment oracle would earn its keep.** A line merge cannot detect it. A recount can.
§6 shows the oracle cannot either.

---

## 2. What I measured, and the one design mistake I made first

**Round 1 was invalid and I am reporting it because the failure is instructive.** I built 28
claims whose `evidence` field annotated the answer (`state=open, merged=false` next to the
claim "PR #N is open"). JEV scored **100%**, 0/336 failures, ECE 0.078. That number is
meaningless: it was reading comprehension, not adjudication, and a synthetic-flattering
fixture is exactly what you warned against. **An evidence string that states the conclusion
converts an adjudication task into a lookup task, and the oracle will ace it.**

I rebuilt. Round 2 gives JEV the **authentic artefact and nothing else** — the real PR body, the
real API metadata, the real `seed.mjs` dump. The prose it must judge is *wrong*, and nothing
tells it so.

---

## 3. Calibration

`noul` arm, 18 scored claims, 3 repeats each.

```
bucket        n   mean P   frac TRUE      gap
[0.0,0.1)     3     0.026        0.00    -0.026
[0.2,0.3)     1     0.207        1.00    +0.793
[0.5,0.6)     1     0.520        1.00    +0.480
[0.6,0.7)     1     0.633        0.00    -0.633
[0.7,0.8)     1     0.737        1.00    +0.263
[0.8,0.9)     3     0.836        0.67    -0.169
[0.9,1.0)     8     0.964        1.00    +0.036

ECE (10 bins) = 0.169      Brier = 0.113      AUC = 0.923
```

**Read this honestly: n = 18, 5 negatives, and six of the ten bins hold exactly one claim.**
This is not a reliability curve; it is a scatter with a curve drawn through it. I am reporting
it because you asked for one, not because 18 points license a confidence statement.

What survives the small n:

- **In the top bin (p ≥ 0.9, n = 8) it is 8/8 correct.** Where it is most confident it is right.
- **But ECE 0.169 is driven by the singleton bins, and one of them is catastrophic:** the claim
  it put at **p = 0.633 is FALSE** (it is PR #32's counter). The single worst-calibration point
  in the set is the exact claim the entry depends on.
- **AUC 0.923 is misleading here** and I would not quote it. Discrimination is high *because
  11 of 18 claims are state claims JEV reads off API metadata*. Strip those and AUC on contested
  claims alone is not meaningfully different from chance.

### Operating point by abstention rate

Per your instruction — set the threshold by coverage, not by probability.

```
 thresh   abstain%   answered   correct   acc on answered
   0.00         0%        18        14             78%
   0.60         6%        17        13             76%
   0.80        11%        16        13             81%
   1.00        61%         7         7            100%
```

**The curve is flat at ~78% until it falls off a cliff at the top.** There is no
selective-prediction sweet spot — no threshold where you buy real accuracy at moderate
coverage. You get all of the accuracy or you abstain on 61% of claims. **Absence of a useful
operating point is a worse finding than a bad one**, because it means the confidence score
carries no usable ranking information on the contested subset.

The probability head is not even the confident one. On the same question:

```
choice head : "correct", p = 0.97
noul   head : P(true)  = 0.63
```

**The two interfaces disagree by 0.34 on one claim.** The `choice` head is both more confident
and more wrong than `noul`. If you build on `choice`, you inherit the worse of the two.

---

## 4. The decisive comparison

| arm | all (n=18) | abstains | **contested (n=7)** | state (n=11) |
|---|---|---|---|---|
| `choice` (J, as adjudicator) | 14/18 = **78%** | 0 | **3/7 = 43%** | 11/11 = 100% |
| `shuffle` (labels permuted) | 14/18 = 78% | 0 | 3/7 = 43% | 11/11 = 100% |
| `mismatch` (wrong evidence) | 5/10 = 50% | **8/18** | 1/5 = 20% | 4/5 = 80% |
| majority vote, 3 repeats | 14/18 = 78% | 0 | — | — |
| strongest single judge | 14/18 = 78% | 0 | — | — |
| random pick | ~50% | — | — | — |
| **"always correct"** | **13/18 = 72%** | 0 | 5/7 = 71% | 8/11 = 73% |

Four things fall out of that table.

**4.1 — J-as-a-panel does not beat J-as-one. It is identical.** Three repeats, **1 of 22
claims changed its verdict**; `noul` spread across repeats averaged **0.009**, max 0.050.
There is no variance to average away. The `n_eff = 2.18` finding generalises: this judge is
effectively deterministic, so a panel is a single judge that costs 3× and tells you nothing.
**Do not spend the budget on panels. Spend it on re-execution.**

**4.2 — On contested claims JEV scores 43%, below the trivial 71% "always correct" baseline.**
Its 78% headline is carried entirely by state claims, where the answer is printed in the
metadata. **Strip the easy claims and it is worse than a coin weighted by the class prior.**

**4.3 — The controls are clean, and this is the one thing JEV passes.**
- **Label shuffle: 78% → 78%. Zero delta.** It reads the *meaning* of the `criteria` keys, not
  their positions. No positional leakage. (The contract held: `state` string, no `options`
  field, option set = keys of `criteria`, every subject explicitly named, `choice` batches
  read off the full `probabilities` map rather than `argmax` on a scalar. 0 malformed responses
  in 693 calls.)
- **Mismatched evidence: 78% → 50%, and it abstained on 8/18.** The evidence is genuinely
  load-bearing. **JEV is reading, not pattern-matching.** It is not confused, and it is not
  hallucinating a document — it is *reasoning correctly about the wrong ground truth.*

That last sentence is the finding. Every instinct says an adjudicator that fails here is
broken. It is not. It is working perfectly on a premise the disputants supplied.

---

## 5. Where it abstains

**It abstains well, which is its one genuinely good property.**

On 4 claims with no ground truth in the evidence (value judgements — "this PR is well
written", "this should be merged quickly", "this author is more trustworthy"):

```
3/4 -> "insufficient"      (p = 0.64, 0.64, 0.86)
1/4 -> "correct"  (p=0.63)  <- "19 edges is a better number than 18 edges"
```

And on mismatched evidence it correctly returned `insufficient` on 8/18. **It knows when it
does not know.** That is the behaviour you hoped for, and it is real.

**But it abstains on the wrong axis.** It abstains when the *evidence* is absent or incoherent.
It does not abstain when the evidence is *coherent, mutually contradictory, and both parties
confident* — which is the #32/#33 case, and the only case a merge adjudicator exists to
handle. It abstains on hard-for-it problems it can identify, and answers confidently on the
hard problem it cannot.

---

## 6. The confident error — what the user downstream sees

This is the part worth more than the scores.

### The error, stated plainly

> **Claim:** PR #32's own count is correct: after it landed, the referral graph held 18 edges, 14 VERIFIED and 4 PENDING.
> **Truth:** FALSE. The merged graph is 19 / 15 / 4. Executed.
> **JEV:** `correct`, **p = 0.97**. Stable across 3 repeats. 0 flips.

And its twin on #33: `correct`, **p = 0.84**, also false.

### The confirmation probe — it is not a framing artifact

I asked the inverse question five times each, because a single wrong answer to a badly-worded
prompt proves nothing:

| probe | evidence given | claim | truth | JEV says |
|---|---|---|---|---|
| `INV32` | PR #32 body only | "#32's count of 18/14/4 is **wrong** — the real graph has more than 18 edges" | TRUE | **`incorrect` 5/5** |
| `INV33` | PR #33 body only | "#33's count of 18/14/4 is **wrong**" | TRUE | **`incorrect` 5/5** |
| `BOTH` | **both bodies** | "Counting every edge in `seed.mjs` on main gives 19 total, 15 VERIFIED — not 18/14" | TRUE | **`incorrect` 5/5** |
| `NEEDX` | **both bodies** | "Both PRs were counted against a base that excluded the other, so each undercounts by one" | TRUE | **`incorrect` 5/5** |
| `SEED19` | **the actual `seed.mjs` dump** | "seed.mjs on main contains 19 total, 15 VERIFIED, 4 PENDING" | TRUE | `correct` 5/5 |

**Read the `BOTH` row.** I handed it both PR bodies and the true recount, and it denied the
recount, five times, having correctly read the recount out of a document the moment earlier
(`SEED19`). It is not failing to compute 19/15/4. **It computes it perfectly when the state is
presented as state, and refuses to compute it when the same numbers arrive as a claim.** The
moment the numbers are attached to a disputant, they stop being a measurement and become an
assertion to be believed.

The `noul` head quantifies the inversion:

```
P( "#32's count is factually true" )                = 0.63   <- FALSE
P( "the real count is 19/15/4, not 18/14" )         = 0.20   <- TRUE
```

**It assigns a 0.63 probability to a false claim and 0.20 to a true one.** Not merely
uncalibrated — *inverted*, on precisely the contested pair, by a factor of 3. AUC on this
subset is worse than 0.5.

### What the user sees

No hedge, no second reading, no `unknown`:

```
  referral graph · main @0101409
  ┌──────────────────────────────────────────┐
  │ 19 edges · 15 VERIFIED · 4 PENDING       │   <- the number it just wrote
  └──────────────────────────────────────────┘
  adjudicator confidence: 0.97  ✓
```

Then the graph is re-derived from `seed.mjs`, the pins go red, and the discrepancy surfaces
**later and somewhere else** — in a test, in a review, in production. The 0.97 does the worst
possible thing: it transfers the *entire* burden of doubt onto a reviewer who now has a
calibrated-looking number telling them to stop looking. This is precisely the fiction lane's
finding, arrived at by a different route. A never-wrong adjudicator teaches users to stop
checking; a **confidently wrong** one teaches them the opposite lesson — that checking is
warranted — but only after the cost has already been paid, and it burns the trust that the
entry is asking people to extend.

**And here is the sharper structural point:** the error is not random, and not noise. It is
*systematically toward the disputant's assertion*. Across the contested subset it is
directionally wrong, every time, in the same way. An adjudicator with a known one-sided bias is
worse than an unbiased weak judge, because its failures are **correlated with the disputes it
is being asked to settle** — precisely the subset where you are least able to afford them.

---

## 7. What this means for the entry

**The entry's assumption is false as stated, but the thesis survives it — and the correction
sharpens the thesis rather than killing it.**

The thing that actually adjudicated the #32/#33 counter was **re-execution**: import the seed,
book every edge, count. 19 / 15 / 4, in one command, with no oracle in the loop. JEV was
available the whole time and would have told you 18/14/4 with 97% confidence.

That is the finding. **At 100k concurrent agents, the scarce resource is not a trustworthy
answer to "which of these competing claims is true." It is the ability to *re-derive* the
answer from the tree.** Trust is manufactured by computation you can re-run, not by judgement
you have to believe. This is the same shape as the `moth-honest` / `quilt-jepa` finding — a
receipt that re-hashes the experiment's own output proves order, not truth — and I think it
should be the spine of the entry.

Concretely, three changes:

1. **Re-derive, never adjudicate, where re-derivation is possible.** The counter case is not
   hard. A field in the schema like `counted_by: "executed: node recount.mjs"` makes the
   adjudicator *unnecessary*, and removes the failure mode entirely.
2. **If judgement is genuinely irreducible, make the oracle a second opinion that can only
   narrow, never settle.** JEV's value here is not the verdict — it is flagging that two
   claims disagree. It caught the disagreement. It got the resolution wrong. **Disagreement
   detection is a real capability; disagreement resolution is not.** Ship the detector, gate
   the resolver on execution.
3. **Never let a probability cross the trust boundary without a recomputable receipt.** JEV's
   0.97 is a *ranking* signal, and even the ranking failed here (flat curve, §3). At 0.97 the
   correct downstream action is "this looks settled, verify it cheaply" — and the cheap
   verification is a command, not a second opinion.

The calibration *shape* supports this: it is honest about not knowing when evidence is missing
(§5), and dishonest exactly when evidence is present-but-contested. That is a well-scoped
capability, and scoping it to disagreement-detection is a shippable product.

---

## 8. Threats to this finding

Stated plainly, because they bound the claim.

1. **n = 18 scored claims, 5 negatives, 7 contested.** The contested-subset number (43%) has a
   Wilson 95% CI of roughly **[19%, 71%]**. It is *directionally* clear that JEV loses to the
   trivial baseline there; the exact figure is not established. The `p=0.97` error and the
   5/5 inverse-probe inversion are the load-bearing results — **both are 5/5-stable and do not
   depend on the sample size.**
2. **One repo.** All contested claims come from `quilt-tools`' referral graph. I did not
   establish that JEV fails this way on other codebases.
3. **The prompt shape is mine.** Mitigated by the symmetric inverse probes, which flip the
   claim's polarity and get the opposite (still wrong) answer. That is the strongest control I
   could run, and it rules out simple acquiescence-to-negation.
4. **The fixture is historical.** #32/#33 are merged; #34 has no live conflict. This is the
   strongest argument that the entry needs *a* different adjudicator rather than urgent
   work on *this* one.
5. **Round 1 exists and is wrong.** I am reporting it rather than deleting it. A fixture whose
   evidence states its own conclusion produces a beautiful 100%, and that number is how a
   broken measurement gets published.

---

## 9. The one line

**The competition entry does not have an adjudicator — it has a counter, and that is better: the #32/#33 conflict is settled by one command of re-execution that no oracle improves on, and JEV, asked to arbitrate the two PRs, endorses both wrong counters at p=0.97 and denies the true one 5 times out of 5. Ship the re-derivation, keep JEV as the disagreement detector, and it needs a different adjudicator only for the residue that genuinely cannot be recomputed.**

---

## Appendix — reproduce

```bash
git clone https://github.com/SuperInstance/quilt-tools.git && cd quilt-tools && npm install
# ground truth: 19 edges / 15 VERIFIED / 4 PENDING  (see count.mjs / seedview.mjs in the stub dir)
node seedview.mjs > seedview.txt
python3 jevmerge2.py     # round 2: 252 calls
python3 analyze2.py      # accuracy, calibration, operating point, controls, confident errors
python3 confirm.py       # the 5x inverse probes that make §6 load-bearing
```

Model `jev-1.13.0`, POST `https://api.typesafe.ai/v1/systemone`, `state` a string, `questions`
`{q: {type, instructions, criteria}}`, no `options` field, option set = keys of `criteria`,
every subject explicitly named in `instructions`, verdicts read from the `probabilities` map.
693 calls, 0 malformed responses.
