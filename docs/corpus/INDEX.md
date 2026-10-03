# INDEX — what exists, what state it is in, and what is not verified

2026-10-01. A single session produced 55 reports and 1.3 MB of artifacts. This
file exists because **a directory of reports is not documentation**, and because
several of the reports contradict each other, one of them corrects another, and
one of them corrects *me*.

Read the states before the claims. Nothing here is a conclusion until its state
says `VERIFIED`.

---

## The four documents that carry the argument

| document | what it is | state |
|---|---|---|
| **`DOCTRINE.md`** | the corrected doctrine, with every claim carrying the measurement that supports or breaks it | SYNTHESIS |
| **`EXPERIMENTS.md`** | four experiments I ran myself, with the errors I made in each | VERIFIED, with self-corrections |
| **`NEXTGEN-GIT-CONCURRENCY.md`** | what actually breaks in git at 100k concurrent agents | ANALYSIS |
| **`MISSION-STEERING.md`** | where the whole thing is going, and the panel measurement that shaped it | SYNTHESIS |

## Corrections, which are the most important documents here

| document | what it corrects |
|---|---|
| **`CORRECTION-PROJECTION.md`** | my own published ladder. A max over four learners at n_eff 1.48; the ordering **reversed** under the median |
| **`FORK-VS-CHAIN.md`** | my own prediction that forking would beat chaining. It does not |
| **`EXPERIMENTS.md` §5** | my own quilt script, which used the exact random split I have been warning against and reproduced the failure immediately |
| **`RELAY-SELECTLIB.md`** | the competition entry's adjudicator premise, refuted by two independent measurements |
| **`BOARD.md`** | the public ledger of what I owe |

**Four of these correct me. That is the point of the set.**

## Experiments — mine, with exact ground truth

| # | question | result | state |
|---|---|---|---|
| 1 | how much of an exact Connect-4 value survives different observations? | lossless 0.8831, colour-collapsed 0.8947, irreversible hash 0.5103 | re-checked, no max-selection |
| 2 | can a check that cannot fail detect anything? | a perfect instrument scored 0.242 because I divided by the wrong denominator | self-corrected |
| 3 | do chains or forks of models buy independent thinking? | no. n_eff 0.165–0.201 across four topologies | VERIFIED |
| 4 | does a quilt gain independence from evidence or from judges? | no. 0.17 vs 0.15, inside the noise | **prediction refuted** |

Ground truth throughout is `SuperInstance/connect4`, 54,166 positions, digest
`0x4ef8351a5c319637`, cut to a subset that passes gravity, balance, subset and
an independent immediate-win cross-check.

## Lane reports, by what they establish

**Audits that found real defects**
- `papers-ROOT.md` — the conservation paper's architecture has **no code, any spelling**: `AdaptiveLayerController` 3 prose, `PermutationTensor` 2 prose, `update_certainty` 1 prose, `BattenSpline` 10 prose
- `sprint-FAILOPEN.md` — 13 repos fail open, 11 share one `try/except`
- `ci-LANE.md` — 23 workflows that cannot fail, 18 are `echo` placeholders
- `RESOLVER-FIELD.md` — the live service in the field
- `syn-CLAIMSTATE.md` — live edge schema vs repository claims

**Lanes that corrected something, including me**
- `syn-AUDITORS.md` — n_eff over the fleet's own reports; found my max-selection
- `PLAYTEST-OUTSIDER.md` — I predicted 3–4 tools clear the bar; it found 1 clean and 1 partial
- `JEV-MERGE.md` — the adjudicator does not work, two ways
- `doctrine-RECHECK.md` — the reversed ordering

**Fiction, used as a falsification instrument**
- `FICTION-COMPACTION.md` — an agent loses its context and keeps the diff. A witness log that records answers but not questions is complete and useless
- `FICTION-FAR.md` — two futures and what they reveal

**Strategy and the future**
- `MISSION-STEERING.md`, `NEXTGEN-GIT-CONCURRENCY.md`, `SCOUT-QUILTINGIT.md`, `SCOUT-JEVNET.md`, `RELAY-SELECTLIB.md`
- `PR-STEWARD.md`, `SHED.md` — the queue and what the fleet should stop doing

## Live surfaces

- **`https://fleet-resolver.prong-potassium.workers.dev`** — the claim resolver, deployed, no auth. Resolves every `path:line` against a real 477-repo / 85,990-file index and recomputes numeric claims from their own stated operands. **Known gaps documented in the service: backticks required, org/repo paths unsupported.**
- **44 D1 databases, 467 tables, 26 non-empty, 18 inaccessible and not yet explained.** `INACCESSIBLE` is not `EMPTY`.

## The three things that are NOT settled

1. **The CRDT layer.** 8 ports, 5 byte-identical, `merge` a no-op in 3,
   `remove` never tombstoning in 3, and a canary that never constructs one.
   `crdt-CANARY.md` is the lane that decides this and it is still running.
2. **`demotion_receipts`** in a live D1 table. A witness record for a claim
   leaving canon. **A table name is a hypothesis about behaviour, not evidence
   of it.** The write path is unverified.
3. **The competition entry.** Its adjudicator is measured not to earn its place
   and `quilt-in-git`, a sibling project in this same account, answers the same
   brief differently. Whether they compose is open, and `SCOUT-QUILTINGIT.md` is
   answering it.

## How to read a claim in this repository

Every number carries one of three states, and the state is part of the claim:

- **measured here** — I ran it, and it is reproducible from a script in this tree
- **cited** — a number from a primary source I opened, with the URL
- **asserted** — a claim in a lane report I have not independently reproduced

The most common failure in this fleet's history is treating an **asserted** as a
**measured**, and this repository is not exempt.
