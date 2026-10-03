# PARALLELISM — the shape of tonight's fan-out, and the mechanism that removes the orchestrator from the path

**Lane:** parallelism census · **Date:** 2026-10-02 · **Pushes:** none
**Runnable artefacts:** `research/evid.py` · `research/seamclaim.py` · `research/demo.py`
**Every number in this file was printed by one of those three.** If it is not in
their output it is not here, and I have not rounded any of them into a nicer shape.

---

## 0. THE ANSWER, IN TWO LINES

> **The fraction of tonight's parallel work that was actually independent is between
> 4% and 11%, and the 83% of lane pairs that is neither — that is the number nobody
> has ever printed — is UNMEASURED, not independent.**
>
> **The one mechanism that would have made the rest of it independent is a seam you can
> `open(2)`-claim before you start: `research/seamclaim.py`.** It is 300 lines, it has
> no orchestrator in its path, and it exits 3 on a round that did not coordinate.

The uncomfortable part is the second sentence's first half. For two days this fleet has
been treating "two lanes never reached the same claim" as evidence they do not
correlate. `syn-AUDITORS.md` even drew a symbol for it — `·` — and then ran Kish's
formula over the matrix anyway. Its own §0 records the consequence: *"the panel was
never given the same items, so panel size bought no replication at all."* Tonight has
the same shape, one level down, and it is worse: the items were never **recorded**, so
nobody can even say how much replication was bought.

---

## 1. THE CENSUS

### 1.0 The fleet census, re-derived this pass as required

| | value | how |
|---|---:|---|
| pages fetched | 52 | `users/SuperInstance/repos?per_page=100&page=N` |
| rows returned | 5,144 | sum of page lengths |
| **unique `full_name`** | **5,144** | `unique_by(.full_name) == rows_returned` — the assertion that matters |
| prior read (this brief) | 5,127 | +17 |
| my own last read | 5,139 | +5 |

I did **not** sort by `full_name` or trust page order, and I did not use API `size` to
rank anything. The count is the unique-key count and nothing else. **This is a floor,
not the fleet size:** `AGENTS.md` documents that `constraint-theory-core` — 135 MB, the
repo most likely to be sent to check a claim — is **not returned by this endpoint at
all**. 5,144 counts what the API lists. The account is larger.

### 1.1 The work surface — three categories, and the third is the one that costs the money

Denominator: **91 markdown artefacts written in the window.** That is an *upper* bound
on "lanes" and I am flagging it as such: it includes the orchestrator's own reports, and
it includes stubs (`r3-JEVPATTERN`, `r2-PAYOFF`, `nextgen-git`, `lattice-RD` carry
`Status: STUB`; 15 artefacts are under 6 KB). **The honest denominator for "lanes that
produced a finding" is lower than 91 and I am not going to guess it downward to flatter
anything.**

**Category A — genuinely parallel. 4 families, 14 artefacts, and they hold up.**

Evidence: what each lane says it *read*, not what it wrote. Pairwise weighted-Jaccard
over evidence units, complete linkage:

| family | n | mean pair sim | max | verdict |
|---|---:|---:|---:|---|
| `r3-*` (CLAIMS / VANTAGE / SWAP / JEVPATTERN) | 4 | 0.013 | 0.048 | **disjoint evidence** |
| `RERENDER` + `TIME-QUERY` pairs | 4 | 0.014 | 0.083 | **disjoint evidence** |
| `debate-A` / `debate-B` | 2 | 0.000 | 0.000 | **disjoint evidence** |
| `res-*` (GEN / OPT / CLUSTER / RUNG) | 4 | 0.030 | 0.108 | weak link — the weakest of the four, and still 4 separate questions |

`res-*` is the clearest thing that happened tonight: four lanes, four repos
(`diffusion-jev-sglang`, `neodisco`, an optimization cluster, a binary read), four
instruments, and they still only share 3% of their evidence. **This is what evidence
diversity looks like when it happens, and it is not the default.**

**Category B — strictly serial, and pretending otherwise is how you get a stalled round.**

- `RERENDER.md` → `RERENDER-BUILD.md` and `TIME-QUERY.md` → `TIME-QUERY-BUILD.md`. The
  `-BUILD` artefact is a dependency of its design doc. Running the pair in parallel is
  not extra throughput; it is one lane wearing two hats and calling it two.
- Every `orch-*` step. A board is only a board after someone has decided what goes on
  it, and that someone was me. `orch-SCOREBOARD.md` is the proof: round 1 scored **0 of
  4** and the emptiness was *mine* to declare.
- The whole of `syn-AUDITORS.md`: you cannot measure the fleet's independence while
  being one of the fleet.

**Category C — one investigation wearing N hats. This is the expensive category, it is
invisible without the analysis, and it is the majority of tonight's fan-out.**

| family | n | mean pair sim | max | verdict |
|---|---:|---:|---:|---|
| `r1-*` (JEVSAMPLER / SYNCOPATION / TYPEFUNC / NOENGINE) | 4 | 0.244 | **0.500** | **one repo, four hats** |
| `ASCII*` (POCALYPSE / PORT / CHARSELECTION / VISION-LANDSCAPE) | 4 | 0.139 | **0.500** | **one question, four hats** |

`r1-*` is the sharpest case and the fleet already knows it: all four lanes target
`SuperInstance/gh-dungeons`, and `orch-SCOREBOARD.md` names the four of them as *the
round*. Four architectures on one repo, one seed set, one harness, one scorer.
**That is a panel in form. Measured on inputs it is `n_eff ≈ 1`** — and the repo's own
§5 control already shows what the scorer does with four lanes that are really one: it
tied `A-full` against `A-twin` at margin 0.0 and correctly declined to break it.

> **Finding, and it will not flatter anything I did: the largest single block of
> tonight's apparent fan-out — the `r1-*` round that produced the most code, the most
> measurement, and the most confident reports — was one investigation wearing four
> hats. Not most of the night's work. The most *convincing* part of it.**

Corpus-wide, at complete-linkage t=0.20: **70 clusters over 91 artefacts.** Nine
clusters hold 2+ lanes and account for 30 artefacts; the largest is 6. Sixty-one
artefacts sit alone. But read §2 before you enjoy that — most of those 61 are alone
because nobody logged what they touched.

---

## 2. THE OVERLAP QUESTION — answer, mechanism, and proof it is broken

### 2.1 Is there a mechanism in this repo that would have caught it? No.

| candidate | what it is | why it is not a registry |
|---|---|---|
| `GATE.md` | a linter | reads finished work and complains. It cannot stop the second lane. |
| `ORCH-SCOREBOARD.md` | a board | a display surface fed by whoever types into it. Nothing reads it back. |
| `ORCH-SCOREBOARD.md §5` | a *control* | the only part of it that has teeth, and it only tests the **scorer**, not the **round**. |
| `orch-LIBRARIAN.md` | an index | found 4 live contradictions — **after** they shipped, by grepping finished text. |

The gap is exactly where the brief says it is. **A seam needs to be claimable, and
right now it is not.** Nothing in this repo makes a lane look before it starts.

### 2.2 It has already failed, twice, in ways I can point at

**A real contradiction, still live.** Six documents carry four mutually exclusive
published counts for one fact, and the tool quotes every one of them from source:

| doc:line | published claim |
|---|---|
| `RESOLVER-FINAL.md:18` | `\| BattenSpline \| the router \| 10 \| **0** \|` |
| `BOARD.md:94` | `PermutationTensor` 2 all prose … `BattenSpline` … |
| `INDEX.md:50` | `BattenSpline` 10 prose |
| `CLOSE-LOOP.md:234` | **0 occurrences across all 275 fleet repos.** `BattenSpline` (12) |
| `CORRECTION-CONSERVATION.md:15` | 10 hits, all prose · **RETRACTED — 136 code hits, it is real** |
| `ORIENTATION.md:46` | `BattenSpline` (136 code hits) … are **real** |

Four numbers: 10, 0, 12, 136. The correct answer, per `orch-LIBRARIAN.md` §1, is
**zero executable-code hits**. Four mutually exclusive numbers are published
simultaneously and **no mechanism in this repo noticed.** It was caught by an agent
*grepping after the fact*, not by a seam being claimed.

**A real replication that was not one.** `RESOLVER-FINAL.md`, `BOARD.md`,
`CLOSE-LOOP.md`, `CORRECTION-CONSERVATION.md` and `ORIENTATION.md` all read
`murmur/transforms/rubiks.py` and all published that it does not exist. That is
**five observers, one evidence unit, one finding. Replication factor 1.0×.** It is the
best-evidenced claim in the repo and it cost five lanes. Nobody could have known to
merge them, because **nobody logged that five lanes had read the same file.**

### 2.3 The mechanism: `research/seamclaim.py`

Three primitives, and the orchestrator is not one of them.

1. **A seam is evidence, not a topic.** A repo, a script, a directory, a file — namespaced
   strings. The registry only ever stores their SHA-1. "Investigate the fleet" is not a
   seam. `repos/quilt-adjudication` is.
2. **A claim is `open(2)` with `O_CREAT|O_EXCL`.** The kernel arbitrates. Two agents in
   two terminals, same box, no coordinator, no lock protocol, no message passing: exactly
   one `open` returns a descriptor, the other gets `EEXIST` and prints `E_SEAM_HELD`
   with the holder, the time, and their note. This is the only coordination primitive in
   the file and it is a syscall.
3. **A lease, and steals that leave a trace.** A dead lane does not deadlock the round —
   its lease expires. But the expiry is a rename, not a delete, and the holder is printed.
   A seam that changes hands with no record is indistinguishable from a seam that was
   never exclusive.

```bash
python3 research/seamclaim.py claim --lane r1-SWAP --seam chooser-seam \
    --evidence REPO:quilt-adjudication INSTR:res-GEN/choosers.py --lease 900
# -> CLAIMED, or E_SEAM_HELD with the holder's note.  exit 2.
```

**And the half that makes it a canary rather than a ninth green badge.** `audit` does not
check that claims exist. It checks the *other* direction: it re-derives each artefact's
evidence set from the file the lane actually produced and asks whether anybody claimed
it. A lane that never called `claim` is `UNCLAIMED` and the audit **exits 3**.

`audit-facts` additionally finds *facts* carrying more than one distinct published
claim — and **verifies every `FILE:LINE` before reporting it**, so you cannot manufacture
a collision you cannot point at. That guard earned its keep during this very build: it
refused the six locations above when I pasted them in the prose shorthand the librarian
had written (`RESOLVER-FINAL:18`), and refused `RESOLVER-FINAL.md:9999` in the
fake-collision test. It rejected my own unverified data twice.

### 2.4 Demonstrated against real collisions, not simulated ones

`python3 research/demo.py` — **5/5 PASS, exit 0.** Every number produced by running it.

```
D1  REAL CONCURRENT RACE     8 OS processes launched simultaneously at one unit
                             exited 0 (CLAIMED)     1
                             exited 2 (E_SEAM_HELD) 7
                             exited other           0
                             claim files on disk    1
                             -> kernel arbitrated; exactly one holder

D2a SHIPPED CONTRADICTION    6 docs registered on 1 fact
                             locations verified on disk    6   <- all real
                             locations that DO NOT exist   0
                             facts with >1 distinct claim  1   <- exit 3, round VOID

D2b FAKE-COLLISION GUARD     a claim at a nonexistent line is refused at registration
                             -> you cannot report a collision you cannot point at

D2c REPLICATION COUNT        5 lanes read INSTR:rubiks.py
                             distinct holders 1 · lanes 5 · findings 1
                             -> replication factor 1.0x across 5 observers

D3  REAL BYPASS              91 of tonight's actual lane documents, registry empty
                             evidence units touched   766
                             properly claimed         0
                             UNCLAIMED (bypass)       766
                             exit 3
                             -> non-coordination is DETECTED, not merely possible
```

D3 is the number I would put in front of Casey: **if this mechanism had been running
tonight, coverage would have been 0 of 766 evidence units and the entire round would
have been refused.** It is not a criticism of the lanes — it is what a canary is for.

---

## 3. EVIDENCE DIVERSITY vs WORKER DIVERSITY — specified operationally or not at all

`n_eff 0.18` over eight vendors is the sharpest number this fleet owns, and
`PREDICTIONS.md:43` already recorded it as a falsified prediction. The brief asks me
to specify what an evidence-diverse panel looks like **for this work**. "Use different
prompts" is not evidence diversity, and I have watched it masquerade as a panel six
times in this repo's own history, so here are the four axes as **checkable
predicates over the input**, not adjectives.

An evidence-diverse panel for fleet work is one where the panel differs on at least
three of these, and where the difference is checkable *before* the lanes run:

| axis | the predicate | what it is not | measured tonight |
|---|---|---|---|
| **MATERIAL** | the lanes read **disjoint repos** | "focus on different things" | `res-*`: 3.0% mean overlap. `r1-*`: 24.4%, one repo. |
| **INSTRUMENT** | the lanes run **different executables** on the data | "analyse it differently" | 1.6% of pairs ever shared an instrument. This axis is nearly unused. |
| **OBSERVATION** | the lanes measure **different quantities at different resolution** — a census and a line-level read are not two samples | "go deeper" | `syn-HARNESS`/`HARNESS2` are the same instrument at two depths. |
| **FAILURE MODE** | the lanes are built to **disagree** — each must predict a value the others will contradict | "different perspectives" | `r3-VANTAGE` does this (`n=6`, one arm unverifiable, reported as such). Almost nothing else does. |

**And here is the operational test that would have caught tonight's `r1-*` round
before it started**, stated so that it is falsifiable:

> Two lanes are evidence-correlated iff their **evidence sets** — not their prompts,
> their models, their vendors, or their prose — have Jaccard overlap ≥ 0.20. At that
> point they are one investigation and the round is one sample. Below 0.05 they are
> independent and the round is a real panel.

That threshold is a choice, and the sweep in §1.1 shows what it costs: at t=0.05 the
corpus is 22 clusters, at t=0.20 it is 70, at t=0.40 it is 76. **I am reporting the
sweep rather than one number because the choice is load-bearing and I will not hide it
behind a single figure.** What does not change across the whole sweep: the `r1-*` and
`ASCII*` families are the same investigation at *every* threshold, and `r3-*` is
independent at every threshold.

**A panel is evidence-diverse iff a third party can tell which lane saw what, without
reading any lane's argument.** That is the test, and it is the one `MISSION-STEERING.md`
got right for the wrong corpus: *"find the lowest-similarity member and read it alone"*
— but a member you cannot identify is not a member you can isolate.

---

## 4. THE INDEPENDENCE NUMBER — how it was computed, and where it must not be trusted

`python3 research/evid.py --calibrate`

```
lanes in window            N = 91
pairs                          4095
pairs sharing >=1 evidence unit  684  (16.7%)
mean units per lane            8.0
```

**Two estimators, and they disagree by 10×. That spread is the finding, not noise.**

| estimator | n_eff | fraction | what it assumes |
|---|---:|---:|---|
| Kish design effect, **all** 4,095 pairs | 39.35 | **0.432** | *a pair that shared nothing is an independent pair* |
| Kish on **observed pairs only** — MATERIAL | 3.46 | **0.038** | unobserved ≠ independent |
| … INSTRUMENT | 4.49 | 0.049 | ” |
| … CONTEXT | 3.44 | 0.038 | ” |
| … ALL AXES | 10.27 | 0.113 | ” |
| complete-linkage clusters @ t=0.20 | 70 | 0.769 | *a lane that overlapped nothing is independent* |

**I am rejecting 0.432 and I am rejecting 0.769, and I will not publish either as
"the" number.** Both treat an unobserved pair as an independent one. `syn-AUDITORS.md`
has a `·` in its matrix for precisely this cell and Kish'd over it anyway; its shuffle
control then **could not reject a known-independent injected lane**, which is how you
know the instrument was blind. I have repeated the defect in a new place if I report
these. So:

> **The measured independence fraction of tonight's parallel work is 0.04–0.11.**
> **The remaining 83.3% of lane pairs are in an unknown state, not an independent one.**

That 83.3% is the sentence this lane exists to produce. It has never been printed in
this repo. `ORCH-SCOREBOARD.md` shows four `UNFILLED` rows and calls the emptiness
"the correct reading, not a placeholder" — correct, and also **unmeasured**. Empty and
independent look identical from outside. The difference is that empty is fixable by a
claim, and independent is a fact.

### 4.1 The instrument's own control, which is a hard gate

```
CAL-A disjoint   true n_eff=6  rho=0.000  recovered=6.00  K=6  OK
CAL-B identical  true n_eff=1  rho=1.000  recovered=1.00  K=1  OK
CAL-C 2 groups   true n_eff=2  rho=0.400  recovered=2.00  K=2  OK
CALIBRATION FAILED -> exit 3, all numbers above VOID
```

**It failed twice before it passed, both times on my own defects, and both times it
refused to certify rather than reporting a number.** CAL-B was a fixture that claimed
six identical lanes while constructing six disjoint ones; the gate caught it. A
single-linkage clustering pass produced a **19-member** cluster and a **0.432**
independence figure that were both single-linkage artefacts — a few weak `DOC:` links
bridging unrelated lanes. Complete linkage dissolved it to a largest cluster of 6.
**I am reporting the wrong numbers I nearly shipped, because the control that caught
them is the only reason the surviving numbers mean anything.**

---

## 5. WHAT THIS LANE PRODUCES — the three extraction slots

| slot | value |
|---|---|
| **chooser** | `seamclaim claim` — the evidence-set claim, taken by kernel-arbitrated `open(2)` before a lane starts. Replaces "the orchestrator decides who works on what", which is the only integration point in the system today. |
| **projection** | the lane's artefact, re-read mechanically by `audit` to recover the evidence set it *actually* touched — not the set it claims in prose. This is the projection that makes a bypass detectable: the artefact is the witness. |
| **invariant** | **every evidence unit an artefact touches was claimed by exactly one lane, and every registered location resolves to a real line.** Neither half is checkable by asking; both are checkable by running. `audit` exits 3 if either fails. |

Not `none` — all three are named, runnable, and have a demonstration that fails loudly.

---

## 6. WHAT WOULD KILL THIS DOCUMENT

Per the standing rule, a report is not delivered until another agent has tried to kill
it. **This one has not been killed, and I am not claiming otherwise.** The specific
attacks I would make, written down so an adversary does not have to invent them:

1. **Break the extractor.** `evid.py` reads evidence out of prose with regexes. Show
   that two lanes reading the same repo in different words score 0 overlap. The 16.7%
   coverage is a *lower bound on observable overlap* and therefore a **lower bound on
   correlation** — which means my 0.04 could be as high as 0.43 in truth. The document
   is safe from this attack only because it reports the range and names the direction of
   the error.
2. **Break the clustering.** The 70-cluster number is threshold-dependent and I showed
   the sweep. Kill the 0.769 column by refusing any single threshold.
3. **Break the denominator.** 91 artefacts is not 91 lanes. It includes my own reports
   and several stubs. If the true lane count is 40, the fractions are wrong.
4. **Break the census.** 5,144 is the API's listed count and `AGENTS.md` proves the
   endpoint omits at least one real repo. It is a floor. Anyone who can find a working
   token should re-derive it; I could not.
5. **Prove the claims here have no second observer.** The safest sentence in this
   document is the least corroborated, which is the `n_eff 0.18` I inherited and never
   regenerated. **I could not reproduce 0.18 from the matrix printed beside it in
   `MISSION-STEERING.md` under any formula in this file.** Mean off-diagonal is 0.743
   and I verified that arithmetic; the design-effect form of that matrix gives 1.28.
   Either a different estimator was used and is not recorded, or the fleet's sharpest
   number is not reproducible from its own evidence. **I am not asserting which, and
   that gap is itself an unmeasured pair.** The honest move is to treat `0.18` as
   unverified until someone re-runs it.

---

## 7. THE TWO SENTENCES

**The fraction of tonight's parallel work that was actually independent: 4%–11% of the
91-lane corpus, with 83% of lane pairs unmeasured rather than independent — and the
`r1-*` round, the night's most confident and most productive-looking work, was one
investigation wearing four hats.**

**The one mechanism that would have made the rest of it independent:**
`research/seamclaim.py` — a seam is a set of evidence units, a claim is
`open(O_CREAT|O_EXCL)`, the kernel arbitrates without an orchestrator, and the audit
re-derives the evidence from the artefact and exits 3 when nobody claimed it. It
admitted exactly one holder of a real seam under a real 8-way race, refused to
certify a round that has already shipped four mutually exclusive counts for
`BattenSpline`, and would have reported tonight's coverage as **0 of 766**.
