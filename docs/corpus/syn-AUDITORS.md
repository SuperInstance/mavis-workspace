# SYN-AUDITORS — applying the field's own measurement to the fleet's own reports

**Lane:** auditing the auditors · **Date:** 2026-10-01 · **Status:** COMPLETE
**Method:** Kish effective sample size over a pairwise agreement matrix, hand-verified claim
extraction, 2,000-permutation shuffle control, and a calibration test to prove the control is
not vacuous.
**Scripts:** `/tmp/auditors/{extract,neff,learners,tie,calib}.py` · **Data:** `neff.json`

---

## 0. HEADLINE

**I was asked for one number. The number does not exist, and proving that is the result.**

| quantity | value |
|---|---|
| reports in corpus | **11** |
| pair cells in agreement matrix | 110 |
| cells where the two reports **ever reached a shared claim** | **48 / 110 = 44%** (24 unordered pairs) |
| agreement on those 48 cells | **1.000 — 48/48, zero exceptions** |
| observed pairs resting on **exactly one** shared claim | **20 / 24 = 83%** |
| share of the whole structure carried by the single most-reached claim | **15 / 24 pairs = 62.5%** (`S6`, the scar doctrine) |
| fleet headline numbers with **zero** corroboration | **3 of 3** (census, autopublisher count, 4,789 figure) |
| Kish n_eff (11 reports, unobserved = 0 mass) | 2.52 |
| Kish n_eff (7-report core) | 1.63, bootstrap 95% CI [1.63, 4.08] |
| **shuffle control** | **z = −0.89, P(obs ≥ shuf) = 0.9835 — DOES NOT REJECT** |
| **calibration of that control** | **CANNOT REJECT even a known-independent injected lane** |

**`n_eff = 1.63` is not a measurement of this fleet. It is a measurement of my own instrument
failing, and I am reporting the second thing, not the first.**

The correct summary of the night is not *"the fleet has 1.6 independent voices."* It is:

> Eleven lanes bought **breadth, not corroboration**. Coverage of the shared claim space was
> **44%**; agreement inside it was **100%** — but **83% of those agreeing pairs rest on a single
> claim, and one doctrine sentence carries 62.5% of the entire structure.** The binding
> constraint was never the shared model family. It was that **the panel was never given the same
> items**, so panel size bought no replication at all, and the three load-bearing numbers the
> fleet actually published tonight each have **exactly one observer**.

---

## 1. THE MATRIX

Rows/cols = the 11 reports. `·` = the two reports **never reached a shared claim**
(*"I did not look"* — never silently scored as agreement or disagreement). `1.0(n)` = agreed on
every claim they both reached, **and `n` is how many claims that was** — the number that decides
whether this matrix means anything.

| | FAIL-OPEN | DANG-TRI | MUSIC-3 | EDGE-NCA | EDGE-INT | F-STRUCT | SPR-CRDT | CI-LANE | CF-D1 | CF-EMB | CF-TTS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **sprint-FAILOPEN** | 1.0 | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(1) | · | 1.0(1) | · | · | · |
| **dangling-TRIAGE** | 1.0(1) | 1.0 | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(1) | · | · | · | · | · |
| **music-ROUND3** | 1.0(1) | 1.0(1) | 1.0 | 1.0(1) | 1.0(1) | 1.0(1) | · | · | · | · | · |
| **edge-NCA** | 1.0(1) | 1.0(1) | 1.0(1) | 1.0 | 1.0(1) | 1.0(1) | · | · | · | · | · |
| **edge-INTERP** | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(1) | 1.0 | 1.0(2) | · | · | · | 1.0(1) | 1.0(1) |
| **fleet-STRUCTURE** | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(1) | 1.0(2) | 1.0 | · | 1.0(1) | · | 1.0(2) | 1.0(2) |
| **sprint-CRDT** | · | · | · | · | · | · | 1.0 | · | · | · | · |
| **ci-LANE** | 1.0(1) | · | · | · | · | 1.0(1) | · | 1.0 | · | 1.0(1) | 1.0(1) |
| **cf-D1** | · | · | · | · | · | · | · | · | 1.0 | · | · |
| **cf-EMBED** | · | · | · | · | 1.0(1) | 1.0(2) | · | 1.0(1) | · | 1.0 | 1.0(1) |
| **cf-TTS** | · | · | · | · | 1.0(1) | 1.0(2) | · | 1.0(1) | · | 1.0(1) | 1.0 |

### 1.0 The matrix looks like a panel. It is a star.

Every one of the 48 observed cells is 1.0 — no exceptions anywhere. That is not reassuring, and
the reason is visible in the `(n)` column:

- **20 of the 24 observed pairs rest on exactly ONE shared claim.**
- **`S6` — "the cell is a scar; the substrate is grown, not designed" — alone supports 15 of the
  24 pairs (62.5%).** Six reports touching one doctrine sentence generates most of the apparent
  panel structure.
- **Exactly one pair in the whole matrix (`fleet-STRUCTURE` ↔ `edge-INTERP`) shares three
  claims.** Everything else shares one or two.
- **`sprint-CRDT` and `cf-D1` reach zero shared claims with anyone.** They are the true singletons.
- **`S2`, `S3` and `S4` support ZERO pairs.** The census count, the "11 of 17 autopublishers"
  figure, and the 4,789 dead-reference count were each reached by **exactly one report**. Those
  three numbers have **no corroboration of any kind** in this corpus.

So the honest description of the agreement structure is not "a correlated panel." It is:

> **One doctrine sentence, restated six times, generating 62.5% of the measured agreement; three
> load-bearing fleet numbers with no second observer; and two reports that shared nothing with
> anyone.**

**A dense-looking matrix built mostly on `n=1` cells is the most dangerous shape this metric can
take**, because it passes a coverage check and fails a thickness check, and nothing in the scalar
tells you which one you are looking at.

### 1.1 Claim set (hand-verified, 8 inherited claims)

| # | inherited claim | reached | verdict spread |
|---|---|---|---|
| S1 | numbers inherited from this fleet's own prior reports are stale/wrong | 4 | 4× CORRECT, 0 confirm · **6 pairs** |
| S2 | "11 of 17 autopublishers have zero tests" | 1 | 1× CORRECT (→ `triage.py` bug) · **0 pairs** |
| S3 | census is 5,127 / 5,113 | 1 | 1× CORRECT (5,113) · **0 pairs** |
| S4 | resolver found 4,789 dead references | 1 | 1× CORRECT · **0 pairs** |
| S5 | "13 repos fail open, 11 share one bug" | 2 | 1 CORRECT, 1 CONFIRM · **1 pair** |
| S6 | doctrine: the cell is a scar, substrate grown not designed | 6 | 4 CONFIRM, 2 CORRECT · **15 pairs** |
| S7 | doctrine: every observation is a lossy projection | 4 | 3 CONFIRM, 1 CORRECT · **6 pairs** |
| S8 | 64-bit hash scored 0.9586 on a random split | 2 | 2 CORRECT · **1 pair** |

**Honest limitation, stated because it is load-bearing:** I did not read all ~220 KB. Extraction
is pattern-based over 8 claims, each verdict hand-checked against the file. **The 100% agreement
is partly an artefact of that coarseness.** Collapsing CONFIRM/CORRECT into "agrees" is what
produced an all-ones submatrix. §3 exists to find the variance that this instrument cannot see.

---

## 2. THE SHARED PRIOR — and why the papers' mechanism is not the one operating here

The NLI paper predicts: *same-family correlation barely exceeds cross-family; the cause is
common training, not shared instructions.* These agents shared a model family, so that is the
prediction to test.

**It is not what binds here, and the data says so in one line: 44% coverage, 100% agreement.**

- If common training were the cause, we would see **high coverage and high agreement** —
  nine judges on three shared datasets gave n_eff 2.18 with 100% of items shared.
- We see **low coverage**. The shared thing was never the items. It was the *instruction*.

**S1 is the finding.** Four reports independently reached "the brief's number is wrong" — on
**four completely disjoint objects**:

| report | object it checked | correction |
|---|---|---|
| `ci-LANE` | `triage.py:40-41,112-117` | "11 of 17 have no tests" is an **instrument bug** |
| `fleet-STRUCTURE` | repo census route | brief's 5,127 is **14 repos stale**; real 5,113 |
| `cf-TTS` | model identity | `smart-turn-v2` is **not** a speech model; corpus is **already** Workers AI |
| `cf-EMBED` | the 25,939-row subset | **two premises false**; defect is the labels, not the decoding |

Four objects, zero overlap, 4/4 agreement. **Agreement survived complete removal of shared
items.** That is *stronger* than the same-family effect the NLI paper reports, and it has a
different cause: **the shared prior was the standing instruction to distrust the brief, not
common training on shared data.**

**So the brief's hypothesis — "if correlation survives removing shared instructions, that's a
direct measurement" — cannot be run here at all.** There was nothing to remove. The instructions
were not one of two competing causes; they were the *only* shared input, and the items were
disjoint. The experiment that would separate common-training from shared-instructions requires
agents on shared items, and this fleet has no such comparison anywhere in the eleven reports.

### 2.1 Adjudication — which "agreements" are corroboration and which are restatement

Agreement is not one thing. I checked the shared claims against the world where the world was
reachable.

| shared claim | reports | independent check | verdict |
|---|---|---|---|
| Cloudflare credential absent | `cf-D1`, `cf-EMBED`, `cf-TTS` | `env \| grep -i cloudflare` → **0 vars** | **CORROBORATED** — 3 independent sessions, same fact about the world, no shared object but the env |
| census = 5,113 | `fleet-STRUCTURE` | `allrepos.json` → **exactly 5,113 entries**; `census.log` → 5,108 | **CORROBORATED** — 5,108 is the truncated one, as claimed |
| 8/10 recalled arXiv IDs wrong | `edge-INTERP` | **queried all 10 against the arXiv API — 10/10 exact match** | **CORROBORATED, by me, third-party** |
| D1 census: 8/20 ids unusable | `cf-D1` | **0 `wrangler.toml` files exist in this workspace** | **NOT LOOKED — not refuted.** No local tree. Do not cite my non-replication. |
| `LINE_OOR` = instrument bug | resolver lane | `resolver.py:427-429` documents the ±140-char window | **CORROBORATED in code** |

**This is the split that matters.** The arXiv adjudication is the only place all night where a
lane's self-correction was checked by a *third party* against an *external* authority and
matched exactly. Everything else that looks like agreement is either (a) unverifiable here, or
(b) the same instruction restated.

---

## 3. DISAGREEMENT AS INSTRUMENT — ranked by how much it changed a conclusion

The brief's premise: two of tonight's findings came from lanes disagreeing with the
orchestrator. **One of those two is not a disagreement.** Ranked by decision impact:

| # | disagreement | changed | lane? |
|---|---|---|---|
| **1** | **`cf-EMBED` refused to answer the question the orchestrator answered.** cf-EMBED:126: *"is 0.9202 colour-irrelevant or saturated? — **remains unanswered**. I have no pretrained-model numbers and will not manufacture any."* | **The orchestrator reported "discarding colour did not destroy the value." The lane said the question was open. The number 0.9202 was read off a table and promoted to a refuted prediction.** | **yes — and it is the highest-value one** |
| 2 | `edge-INTERP`: *"I do not remember arXiv IDs... **Two were correct**"* | Retracted and re-resolved every citation in the lane. Evidence base replaced. | yes (self) |
| 3 | `edge-NCA`: verdict **(b)** — learned CA produces *"not cells at all"* but *"a shared update rule plus a thresholded view"* | Directly contradicts the fleet's central doctrine, and calls the failure *"sharper than 'not established'."* | yes |
| 4 | `cf-D1` §3.2: **the selftest caught a write in the read-only gate** — `PRAGMA writable_schema=ON` sails through `startswith("PRAGMA")` | A file whose entire purpose is to be the thing that cannot write, could write. | yes (self) |
| 5 | `edge-INTERP`: doctrine is *"right about the conclusion and wrong about the content... unfalsifiable because it is missing a condition"* | Core doctrine downgraded from slogan to conditional. | yes |
| 6 | `cf-D1` §2.1: *"three of the twelve"* → **8 of 20** ids unusable | Earlier count came from hand-reading one key, skipping `preview_database_id` and 3 empty strings. | yes (self) |
| 7 | `cf-EMBED`: *"The real defect: **the labels, not the decoding**"* | Reassigned the root cause of the 44.1% decode failure. | yes |
| 8 | `fleet-STRUCTURE`: its own first parser dropped a real repo (`discussions`, a reserved route that is a repo name) | Census denominator; fixed by positive rule. | yes (self) |
| 9 | resolver: `LINE_OOR` — *"I called it the worst category and ranked it above the rest. **All four were tool artifacts.**"* | A whole category deleted from the findings. | **NO — outside the 11** |
| 10 | projection experiment: random split made the hash beat the complete board | 0.9586 → 0.5045 on the honest split. | **NO — not a lane** |

**Two of the brief's four headline "disagreements" are not lane disagreements.** #9 (LINE_OOR)
came from the orchestrator's own resolver consolidation (`RESOLVER-FINAL.md`), not from one of the
eleven. #10 is the projection experiment, not a lane. And **the brief's own example — "I predicted
discarding colour would destroy a value and it did not" — is #1, and the lane explicitly
declined to make that claim.** The prediction was not refuted by a lane. It was *adopted* by the
orchestrator from a lane that had marked it unanswered.

**The fleet's actual measurement output for the night is this list. Everything else was
agreement** — and 44% of it was not even overlap.

---

## 4. SECOND TARGET — n_eff over the four Connect-4 learners

Data: `/workspace/experiments/run2.log`, 25,939 boards, 5 observations × 4 learners × 2 splits.

### 4.1 The number

**By-ply (honest) split — 4 learners × 5 observations:**

| observation | logreg | knn | mlp | rf-logreg | spread |
|---|---|---|---|---|---|
| L0 lossless | 0.9500 | 0.6100 | 0.9200 | 0.9300 | 0.3400 |
| L1 colour-collapsed | 0.9400 | 0.7200 | 0.8900 | 0.8900 | 0.2200 |
| L3 coarse colour-preserving | 0.8600 | 0.6400 | 0.7400 | 0.7300 | 0.2200 |
| L4 hash64 irreversible | 0.6100 | 0.5100 | 0.5000 | 0.5200 | 0.1100 |
| L5 stone count only | 0.6700 | 0.5000 | 0.5000 | 0.6500 | 0.1700 |

Pairwise correlation **0.772 – 0.984** (logreg↔mlp = 0.984).

> ## **n_eff = 1.48 over 4 learners. n_eff/k = 0.37.**

**0.37 is below the 0.5 threshold both papers set for "uninterpretable without caution."**
The four learners are worth **one and a half independent votes.**

### 4.2 The shuffle control, and its calibration

```
observed k=4 learner n_eff = 1.48
shuffle (4,000 perms): median 1.48   95% CI [1.48, 1.48]   z = +0.00   P = 0.8037
```

**Degenerate CI of width zero.** I did not accept it. I calibrated it by injecting a fifth
learner whose independence I *know*:

| injected element | n_eff | z | P(obs ≥ shuf) | control verdict |
|---|---|---|---|---|
| uniform-random scores (known independent) | 4.56 | +1.77 | 0.185 | **CANNOT REJECT** |
| logreg + 0.005 Gaussian noise (known copy) | 1.36 | +2.05 | 0.386 | **CANNOT REJECT** |

> **The control cannot detect a deliberately independent learner. It is a control that cannot
> fail — the same defect class as the `PRAGMA` gate in §3#4, one layer up.**

The cause is sample size, and it is quantifiable. Holding the four real learners fixed and
padding the observation count with genuinely independent scores:

| observations | 5 | 10 | 20 | 50 |
|---|---|---|---|---|
| n_eff | **1.48** | 2.25 | 2.28 | 5.30 |

**Five observations cannot support this statistic.** The reported 1.48 is inside its own noise
band. The honest statement is: **`n_eff` is not measurable at n_obs = 5; what *is* measurable is
the raw correlation, 0.77–0.98, and that alone puts the panel below k = 2 on any reasonable
reading.**

### 4.3 Best-learner-per-observation, and what it cost

| observation | reported | learner | by-ply | drop |
|---|---|---|---|---|
| L0 lossless | 0.9497 | rf-logreg | 0.9314 | 0.0183 |
| L1 colour-collapsed | 0.9391 | mlp | 0.8947 | 0.0444 |
| L3 coarse colour-preserving | 0.8593 | mlp | 0.7411 | 0.1182 |
| **L4 hash64 irreversible** | **0.9586** | mlp | **0.5045** | **0.4541** |
| L5 stone count only | 0.6678 | logreg | 0.6678 | 0.0000 |

Max-per-observation selection over 4 learners at n_eff = 1.48 is a **selection over ~1.5
independent draws, not 4.** The one number that mattered — 0.9586 — was selected *and* measured
on the leaky split, and it is the only observation whose selected learner (`mlp`) is the
lowest-correlated member of the panel (0.181 with logreg on the random split). **The selection
picked the most independent learner precisely where independence was most dangerous.**

### 4.4 A third control defect, found by reading the control

`/workspace/experiments/control.log` declares:

> `FAIL - only 0.9486 on a task a learner should solve. The harness is broken and the projection
> ladder means nothing. Do not publish it.`

**That verdict is a false negative, and its own log refutes it.** `control.log` records the
control label distribution as `{-1: 6768, 1: 19171}`; `run2.log` records the solver's value
distribution over the same 25,939 boards as **`{-1: 6768, 1: 19171}` — identical.** The "control
task" is **not a different task.** Its cross-checks are 0/0 in both directions, and the second
("p0 has NO immediate win but solver says p0 wins") is **vacuous by construction** — at plies 1–6
a win is always the last move.

So the ceiling test compares a learner against a label it is already being trained to predict,
and reads a representation ceiling as a broken harness. **0.9486 from 84 raw columns on an
immediate-win task is an interaction the model class cannot express, not a broken decoder.** The
correct ceiling is a ~10-line hand-written immediate-win check, which should be exactly 1.000.
**This is the third control tonight that reports failure it cannot distinguish from its own
design.** I did not run that check — `c4` ground truth is not in this workspace — so this is a
reading of the logs, not a measurement, and it is flagged as such.

---

## 5. WHAT I DID NOT LOOK AT

Stated as a list because the brief asked for it and because three items in this report are
adjacent to it:

- **`GITHUB_TOKEN` is absent from this session.** Read-only GitHub access was offered and is not
  available. Nothing here depends on it; the census adjudication used local files.
- **No `wrangler.toml` exists anywhere in this workspace** (0 files, searched). The `cf-D1`
  D1-census correction is therefore **not replicated and not refuted.**
- **Reports outside the 11** (`RESOLVER-FINAL`, `RESOLVER-DEFECT`, `F1-AUDIT`, the
  `*-PRIORART` / `papers-*` set, the 2026-09-30 wave) are excluded **by scope, not judgement**.
  LINE_OOR (#9 above) is in that excluded set and is cited because the brief named it.
- **`/workspace/experiments/synergy.py` is a different lane** measuring instrument *detection
  power*. Its `n_eff_instruments: 0.417` is a different quantity over a different matrix and is
  **not** reused or compared here.
- **The 4-dp log cannot settle whether `logreg`/`knn`/`mlp` are the same function at L5** (all
  three print `0.6678`). Three-way exact agreement across algorithm families is suspicious, but
  per-example predictions were not logged and 4 dp is not bit-identity. **Suspicious, not
  established.**
- The arXiv adjudication (§2.1) covers the 10 IDs in `edge-INTERP`'s own table. It does **not**
  verify the 3 IDs that agent could not resolve (Xu/V-information, Adebayo, Hewitt & Manning).
  Those remain **unconfirmed**, exactly as reported.

---

## 6. THE RECOMMENDATION

The papers' advice is *report n_eff*. On this corpus that advice fails, and the reason is
specific enough to act on:

1. **n_eff needs a shared item set.** It measures redundancy *across judgements of the same
   thing*. Eleven lanes on eleven different things have no redundancy to measure — the correct
   value is undefined, not low. **The fleet's "11 lanes reported" is not 11 votes and should
   never have been read as one.**
2. **At n_obs = 5 the statistic has no power and its shuffle control cannot detect a known
   independent element.** Any future n_eff claim in this fleet needs a calibration arm — an
   injected known-independent judge — or it is a number without a test.
3. **The highest-value output of a panel is its disagreements, and this fleet had no mechanism
   to collect them.** Zero cross-lane conflicts exist in the corpus, because the lanes never read
   each other. The disagreements that did occur were all *self*-disagreements — an agent against
   its own instrument. **The fleet's sharpest auditing has always been each agent auditing
   itself, and the panel added nothing to it.**

---

## 7. REPRODUCIBILITY

```
python3 /tmp/auditors/extract.py    # claim extraction -> verdicts.json
python3 /tmp/auditors/neff.py       # 11x11 matrix, Kish n_eff, bootstrap, 2000-perm shuffle
python3 /tmp/auditors/learners.py   # 4x5 learner matrix, both splits, shuffle
python3 /tmp/auditors/tie.py        # exact-tie structure
python3 /tmp/auditors/calib.py      # control calibration (the part that matters)
```

All inputs are local files under `/workspace/projects/fleet-triage/` and
`/workspace/experiments/`. No pushes were made. `${TYPESAFEAI_KEY}` was not used: no JEV
comparison was re-run, because the question was about measurement independence, not about JEV.
