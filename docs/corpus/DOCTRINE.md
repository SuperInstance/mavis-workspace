# DOCTRINE — corrected, with the measurement attached to every clause

2026-10-01. The fleet's standing doctrine has been:

> *"Every observation is a projection. Every projection is lossy. No downstream
> cleverness recovers what the looking never carried."*

It is a good sentence. It is also **unfalsifiable as stated**, and an
unfalsifiable sentence cannot be built on. This is the version that survived
being measured, with the evidence for each clause and the evidence that broke it.

---

## 1. "Every observation is a projection." — **KEPT, with a boundary**

**Held.** A 64-bit irreversible FNV-1a hash of a 54,166-position corpus destroys
everything: median balanced accuracy **0.5103**, spread **0.0122** across four
learners, against a chance floor of 0.5000. That is the tightest result in the
set, and the small spread is why it is trusted.

**The boundary this clause was missing.** Projection does not destroy *structure*
by default. It destroys structure when it removes the structure the task needs.
`L6`, six column heights plus per-column occupancy bits, scored **0.9871** — better
than the lossless 84-column observation at 0.9239, from *less* evidence.

> **Corrected:** what is lost is not information at large, it is the *particular
> structure a downstream learner would have used*. Nothing recovers the one you
> removed; a great deal survives the removal of other things.

## 2. "Every projection is lossy." — **RETIRED as stated**

**Retracted.** A structured projection that discards a *named attribute* keeps
almost everything. Colour-collapsed — the entire ownership assignment, on a label
defined relative to player 0 — came in at **0.8947 median against a
pre-registered prediction of 0.50**, which is 0.3947 above chance.

**The claim that replaced it:**

> **Named loss is cheap. Structural loss is not. And the distinction is
> task-relative, not universal.**

## 3. "No downstream cleverness recovers what the looking never carried." — **KEPT, and sharpened**

This is the clause that has earned its keep, and it is the one the whole
project is built on. It held in every test:

- An **irreversible** hash: nothing recovered it. 0.5103.
- **Aggregation cannot manufacture what was never there.** Dawid-Skene EM and
  accuracy-weighted voting closed **at most 11% of the Condorcet gap, even with
  oracle gold labels** (arXiv 2605.29800). Better aggregation is not more
  evidence.
- **Semantic entropy cannot detect a judge that is confidently wrong.** It
  measures disagreement the model *has*, not error it does not know about, and
  is exactly zero when the model reliably repeats the same wrong claim.

**The sharpening.** The clause is about *evidence*, and it has nothing to say
about *independence*. Section 4 is where I went wrong.

---

## 4. NEW CLAUSE: agreement is not independence

This clause did not exist in the old doctrine and it is the one that was
missing from every system built under the old one.

> **Two things agreeing tells you almost nothing about whether either is right.
> Independence is agreement in the ERRORS.**

**The evidence, six independent measurements, one constant:**

| setting | n_eff |
|---|---|
| 9 frontier judges, 7 vendors, NLI, 100 human annotations/item | **2.18** [2.07, 2.31] |
| 16-vote panel, 330 real A/B tests | **~2** |
| 4 learners on my own experiment | **1.48** |
| 11 of this fleet's own reports | **2.52** (1.63 core) |
| 7 free models, 4 topologies | **0.165 – 0.201** |

**The sharpest single measurement** is that judges agree with **each other** at
**κ 0.74–0.88** while each agrees with **outcomes** at **~0.2**. A panel that
agrees with itself at 0.8 and with reality at 0.2 is a panel whose agreement is
measuring its shared priors.

**And the consequence for this fleet specifically:** the n_eff paper found
same-family model pairs **only slightly more correlated than cross-family pairs**,
pointing to common pretraining as the dominant factor. The advice "mix providers,
not models" is **sound in intent and weak in effect.** A ZAI checkpoint and a
Qwen checkpoint that share a pretraining distribution, averaged, is closer to
sampling one distribution twice than to assembling a panel.

---

## 5. NEW CLAUSE: a cell must earn its independence, and it mostly cannot

> **A quilt of N cells on one question is one cell wearing N costumes.**

Tested four ways, all failing to manufacture independence:

| variation | n_eff of 7 |
|---|---:|
| parallel, one shared prompt | 0.165 |
| chain, each reads the previous | 0.201 |
| fork, branches never merged | 0.179 |
| evidence varied instead of judge | 0.170 |

I predicted that **diversity of evidence beats diversity of opinion.** It does
not; the difference is +0.02, inside the noise. **Retracted.**

**What does hold:** a cell should carry the representation that matches the
decision, not the richest one available. `L6` beat `L0`. `L7` — the squares
owned by *both* players, a nearly-empty set — scored 0.5808, near nothing.

> **Corrected cell rule: a cell earns its place by holding a representation
> matched to the decision it supports. A second opinion on the same evidence
> adds nothing and costs a call.**

---

## 6. NEW CLAUSE: an instrument that cannot fail is worse than no instrument

> **A check that cannot fail is worse than no check, because it buys confidence
> it has not earned.**

Instances confirmed in one session:

- 13 repositories fail open; 11 share one `try/except` in a 6-line file; 10 are `substrate-*` with zero CI
- 23 workflows that cannot fail; **18 are `echo "No CI configured"` placeholders**
- a CRDT canary that **asserts one FNV constant and never constructs a CRDT**
- a witness log that records answers but not questions, which is complete and useless

And the formulation that generalises all of them, from `selectlib` reopening its
own closed conclusion:

> *"I wrote a control that could not pass, then read its failure as a field bug."*

## 7. NEW CLAUSE: a random split lies, and the gap is the finding

> **A random split on data with near-duplicates is not a weaker test. It is a
> different test that reports a confident wrong number.**

- A 64-bit irreversible hash scored **0.9586** on a random split — **higher than
  the complete 84-column observation** — and **0.5045** on the honest by-ply split
- A dataset whose feature is **pure noise** with duplicate observations sharing
  labels scores **1.000 balanced accuracy** on a random split and 0.775 grouped
- **I reproduced this inside my own quilt experiment**, in the same session I
  wrote it up, in a script whose every brief I had written said "never the
  random split." The hash scored 0.9244.

> **The rule that survives: no gap smaller than the spread is a finding.**
> `L0`'s spread across four learners was 0.3209 — twenty-nine times the gap I
> originally published as a result.

---

## What is left standing after all of this

1. Evidence destroyed irreversibly stays destroyed, and no aggregation recovers it.
2. Agreement is not independence; measure `n_eff` or you are measuring your own priors.
3. One cell on one question. Get independence from a different *representation*,
   not a second call.
4. Give every check a way to fail, and prove it fails.
5. Publish the split. A number without its evaluation is a number without a
   claim.
6. Record the question alongside the answer, or the record is complete and useless.

And one condition on continuing any of it:

> **Someone must be able to disagree with the output and be right.** That is the
> one property none of 5,127 repositories currently has, and an instrument nobody
> can contradict is an `echo "No CI configured"` placeholder with a larger index.
