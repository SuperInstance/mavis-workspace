# exp-02 — replacement harness: ground truth as the scorer, and a guard that can hear a *wrong* judge

**Lane:** EXPERIMENTER 02. **Stub at:** 2026-10-02 ~09:00Z (~14 min in; the 10-minute stub
target is missed and I am not going to dress that up).
**Status:** negative controls discharged. One arm measured. **The headline comparison is
NOT measured** — `TYPESAFEAI_KEY` is absent from this lane, so arms A and B are
`UNEXECUTABLE`. That is a fetch failure, which this project classes as `UNVERIFIABLE`, not
as a zero and not as a finding. There is no ledger in this file and there should not be one.

---

## 1. The diagnosis, in the order it matters

**1.1 — The old guard is a presence check wearing the costume of a validity check.**
`any()` over the judge map asks "did a number arrive". It cannot fail on "are the numbers
the same", and it cannot fail on "are the numbers right". exp-01 measured this: 5 of 5
informative judge mutants passed it. I re-measured it against my own build: **the presence
clause alone caught 1 of 6.** The clause is not wrong, it is *one seventh of the question*.

**1.2 — The headline metric was a compile-time contradiction.** `judge_liked_wrong` counts
`s["judge"] >= 4` where `s["judge"]` is a mean over criterion values read out of a field
named **`probabilities`**. A probability is in [0,1]. `>= 4` is unreachable. exp-01 is right
that this is a retraction and it is the more valuable half: the harness's reason for
existing was a number that was provably, statically zero, and it survived a session, a
failure write-up, and a guard written to defend it. **A guard above a metric is not a check
on the metric.** I have not fixed `it_department.py` and I am not re-running it; the
replacement does not use that metric at all.

**1.3 — The structural flaw underneath both, which the mandate names and I now agree is
the real defect: the design scored answers with the component it had measured not to work.**
A judge that is determinism-collapsed, worth ~2 effective votes, and that once emitted a
confident falsehood at p=0.633, was the arbiter of whether another arm was correct. Every
number downstream inherited that. You cannot calibrate a scorer you are simultaneously
asking a question about. **So the judge is gone as a scorer. It stays only as a subject
under test.**

**1.4 — What I am explicitly not doing:** not re-running the old three-arm design, not
patching `judge>=4` and re-reading the same column, and not reporting a score of 0 for an arm
that never ran.

---

## 2. NEGATIVE CONTROL — before any result

The control suite is 6 informative judge mutants plus 1 positive control, run through 4 guard
clauses. **A guard that fires on the positive control is broken, so the positive control is
part of the suite, not a footnote.** All arms are printed by the same run; no credential, no
network.

Guard clauses:

| clause | question it asks | what it is blind to |
|---|---|---|
| **G1** presence (exp-01's) | did a score arrive? | everything else |
| **G2** complete ∧ non-constant | is every cell scored, and is the score matrix not a constant? | a matrix that varies for no reason |
| **G3** shuffle | permute the answers across the slots — does the score vector move? | a judge keyed to content but *wrong* |
| **G4** discrimination | does the judge rank correct cells above incorrect ones (AUC > 0.5)? | a judge that is merely *mediocre*, not directional |

**Result — counts, n = 6 informative mutants:**

```
mutant               G1     G2     G3     G4     verdict    AUC
M1-dead              False  False  True   False  REFUSES    None
M2-constant          True   False  False  False  REFUSES    0.500
M3-partial           True   False  True   False  REFUSES    None
M4-plausible-wrong   True   True   True   False  REFUSES    0.130
M5-length-keyed      True   True   True   False  REFUSES    0.315
M7-slot-heuristic    True   True   False  True   REFUSES    0.870
M6-healthy  (control) True   True   True   True   COMPLETES  0.870

old guard (G1 alone) caught : 1/6
new guard (G1+G2+G3+G4)      : 6/6
```

**The line that is the finding:**

> **`M4-plausible-wrong` passes G1, G2 *and* G3.** It is well formed, non-constant, every
> cell scored, and it *moves* its score under permutation because it is genuinely keyed to
> the content — it is fluent, confident, and wrong, which is exactly the shape of the
> artefact this fleet keeps producing. **Only G4 stops it.** And G4 is only available
> *because ground truth exists* — which is the argument for the redesign, demonstrated rather
> than asserted. A guard suite bolted onto the old design could not have contained M4, because
> the old design had no ground truth to be wrong against.

Three limits I will not paper over:

- **G4 catches a judge that is wrong in a *direction*, not one that is merely mediocre.** A
  judge landing at AUC 0.52 would pass G4. Given n=10 prompts in Part 2, G4 as a gate is
  coarse; it is a floor, not a verdict.
- **G3 cannot be run before ground truth exists, and neither can G4.** Both are downstream of
  the redesign. On the old harness only G1 and G2 were available, which is why 5 of 5 slipped.
- **`M7-slot-heuristic` scores AUC 0.87 and is still caught — by G3.** A judge that obeys the
  rubric perfectly and always likes the third option is *indistinguishable from a good judge
  by its output alone*. Only the shuffle separates it. That is the `JEV-CONTRACT.md`
  instruction to add a shuffle control before believing any judge output, and it is load-bearing.

---

## 3. The bank — 10 prompts, 10 checkable answers

Every gold answer is verified by a command, and **a prompt with no checkable answer was not
admitted.** Verified now, in this lane:

```
CORRECTION-PROJECTION.md :: 'n_eff = 1.48'        -> 1 hit
DOCTRINE.md              :: '13 repositories fail open' -> 1 hit
ORIENTATION.md           :: '48 carry an explicit invariant' -> 1 hit
ORIENTATION.md           :: 'True ratio is **3.296'  -> 1 hit
CRDT-CANARY2.md          :: '2026-09-30'            -> 3 hits
docs/LANES.md            :: '5,111 open to PRs'     -> 1 hit
DOCTRINE.md              :: '11 share one'          -> 1 hit
ORIENTATION.md           :: 'test asserts `>= 16`'  -> 1 hit
live: ls -1 *.md | wc -l              -> 93
live: wc -l < ORIENTATION.md          -> 124
```

P01–P06 are yours. **P07–P10 are mine, for you to check:** P07 = 11 (the `try/except` count
inside the 13), P08 = 16 (the bound that makes the `6.8×` test pass at any value), P09 = 93
top-level reports, P10 = 124 lines. I have flagged which of these are which below so a wrong
gold is cheap for you to find.

Corpus: **103 files, 5,645 paragraph chunks**, BM25 (k1=1.5, b=0.75), top-8, answer extracted
by slot regex from the highest-ranked chunk that yields a candidate.

---

## 4. FIRST MEASUREMENT — arm C (free local lexical) against ground truth

No model. No network. No credential. A census, not a sample.

```
prompt  outcome  predicted      gold          retrieved  source
P01     HIT      1.48           1.48          yes        CORRECTION-PROJECTION.md
P02     HIT      13             13            yes        DOCTRINE.md
P03     HIT      48             48            yes        TYPES-UNLOCKED.md
P04     HIT      3.296          3.296         yes        dir-SECURITY.md
P05     HIT      2026-09-30     2026-09-30    yes        CRDT-CANARY2.md
P06     MISS     None           5111          NO         —
P07     HIT      11             11            yes        DOCTRINE.md
P08     HIT      16             16            yes        dir-SECURITY.md
P09     MISS     202            93            NO         INDEX.md
P10     MISS     02             124           NO         papers-ROOT.md

ARM C CORRECT: 7/10
  of which answerable-by-retrieval: 7/8
  gold string present in top-8 chunks: 7/10
```

**Three misses, and they are three different things — do not average them:**

- **P06 (5,111 open-to-PR) is a real retrieval failure.** The gold lives in
  `docs/LANES.md:19`, outside the top-level chunk set the query surfaced. This is the one
  miss a model arm could plausibly repair, and it is the only prompt in the bank that
  discriminates the arms. **It is therefore load-bearing, and it is one prompt.**
- **P09 and P10 are `command-only`.** Their answers are properties of the *filesystem*, not
  of any document. No retrieval system can touch them, and **neither can a model arm without
  code execution** — a model that guesses `93` and gets lucky has demonstrated nothing. I
  kept them in the bank and labelled the class rather than quietly dropping them, because
  dropping the unanswerable prompts is how a benchmark inflates itself.
- The honest arm-C number is therefore **7/8 on prompts a reader could answer from the text,
  and 0/2 on prompts that require running something.**

---

## 5. What is NOT measured, stated as such

| arm | status | why |
|---|---|---|
| **A_single** (1 JEV call) | `UNEXECUTABLE` | `TYPESAFEAI_KEY` absent from `env` |
| **B_refracted** (3 calls) | `UNEXECUTABLE` | same |
| **BGE-M3 embeddings** | `UNEXECUTABLE` | `CLOUDFLARE_TOKEN` absent |
| **C_free** | **measured, 7/10** | needs nothing |

`credentials: {'TYPESAFEAI_KEY': False, 'CLOUDFLARE_TOKEN': False, 'GITHUB_TOKEN': False}` —
all three verified absent **by name**, not inferred from a failure.

Per `JEV-CONTRACT.md` and the standing rule, I am applying your own warning to my own lane:
**an absent credential and a `TLS EOF` are transport facts, not evidence about the request,
and neither is evidence about the model arms.** I did not call the endpoint. I have no
result on it.

**Your prediction is therefore untested.** I did not run A vs B, I cannot report a direction,
and I will not forecast one from the literature — including not forecasting it from
`n_eff ≈ 2`, because the honest reading of that table is that it predicts noise-climbing,
not that it settles this. If B wins, that is the result worth having and it needs a lane with
a key.

---

## 6. Ledger

**None written. This run does not write one.** The `INVALID RUN` guard is in the code and
there are no numbers here that deserve to be certified: one of three arms is unexecutable,
and the guard suite's own clause G1 is demonstrably insufficient. Writing a ledger now would
be the exact failure mode this lane exists to catch. (Note for whoever runs next: the stale
`/workspace/it_department_ledger.json` is exp-01's 180-byte all-zero receipt, and
`experiments/it_department.py` **does not exist anywhere on this filesystem** —
`find /workspace -name '*it_department*'` returns nothing. exp-01 reports importing "the real
module"; I could not locate it. Flagging, not blocking.)

---

## 7. Reproduce

```bash
python3 /workspace/projects/fleet-triage/exp-02/harness.py     # ~1.5 s, no creds, no network
cat     /workspace/projects/fleet-triage/exp-02/results.json
```

Every count in §2 and §4 is printed by that one command.

---

## 8. The question, answered as far as the evidence goes

> **Does a model arm earn its place over a free local retrieval, on our own material?**

**Not established — and the bar just moved, not down.** Two facts constrain the answer and
neither of them flatters the model arm:

1. **A free local BM25 baseline answers 7 of the 8 prompts a reader could answer, on our own
   corpus, at zero marginal cost.** A model arm does not have to be good. It has to be good
   on P06 — one prompt — by enough to justify a network call, a credential, a flaky
   endpoint, and a scorer that this project has six independent measurements saying is worth
   about two effective votes. **That is a low bar for the model and a high bar for the
   design, and I would rather name it now than discover it at n=10.**
2. **The honest finding of this lane is not an accuracy number. It is that the old harness
   could not have detected its own failure, and the new one can — but only because ground
   truth was made the point.** M4 is the proof: well formed, non-constant, permutation-
   sensitive, confidently wrong, and it sailed through three of four clauses. **A model arm
   that cannot be checked against ground truth has no seat at this table, and neither does a
   judge.**

Run it with a key, and the comparison is one command away. Until then: no number, no ledger,
no soft prediction in either direction.
