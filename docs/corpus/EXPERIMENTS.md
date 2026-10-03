# EXPERIMENTS — four, with the mistakes in them

2026-10-01. Every experiment below was run by me in this session. Ground truth
throughout is exact Connect-4 minimax from `SuperInstance/connect4`, 54,166
positions, digest `0x4ef8351a5c319637`.

**Each section carries the error I made in it.** Three of the four produced a
wrong result first, and in two of those the wrong result was one I nearly
published.

---

## 1. How much of an exact value survives a lossy observation?

**Script:** `experiments/projection_doctrine.py` · **Log:** `experiments/RESULTS.log`
**Control:** `experiments/positive_control.py` · **Log:** `experiments/CONTROL.log`

**Pre-registered before running, including one prediction I expected to fail:**
P1 L0 lossless high; **P2 colour-collapsed ≈ chance**; P3 L3 below L0 and above
chance; P4 hash ≤ L1; P5 stone-count near chance.

**Controls first.** Shuffled labels → 0.5000. Positive control on a *local* task →
0.9486, which is what proved the harness could reach a ceiling at all.

### The result, re-checked and reported without max-selection

| observation | median | spread |
|---|---|---|
| L0 lossless (p0+p1, 84 cols) | 0.8831 | 0.3209 |
| **L1 colour-collapsed (42 cols)** | **0.8947** | 0.1967 |
| L3 coarse, colour-preserving | 0.6839 | — |
| L4 hash64 irreversible | 0.5103 | **0.0122** |
| L5 stone count only | 0.5000 | — |

**P2 failed by 44 points.** I predicted that discarding colour entirely would
destroy a label defined relative to p0. It did not. **It strengthened** — 0.8947
against a pre-registered 0.50 is 0.3947 above chance, larger than the 0.9202 I
originally reported as a maximum.

### The error I made, twice

**The maximum.** I published the best of four learners per condition. A sibling
lane computed **n_eff = 1.48** over those four, so it was a selection over ~1.5
effective votes. The ordering **reversed** under the median: I had published
L0 0.9314 > L1 0.9202, and the median is L0 0.8831 < L1 0.8947. With a spread
of 0.3209 on L0, **no gap smaller than the spread is a finding** — and I broke
that rule on my own headline table. Retracted in `CORRECTION-PROJECTION.md`.

**The metric.** `detection_power` first divided true positives by *all* cases, so
it returned the base rate. A **perfect** instrument scored 0.242 on a
25%-failure set. A metric whose number is not the number its name claims is the
exact failure this project exists to characterise, and I had built one.

### The ground truth has a defect, and the positive control found it

`c4_ground_truth.txt` has **44.1% of rows carrying `pos` bits outside the 42-bit
`mask` space** — `pos` is a 7×7 bitboard, `mask` is 7×6. The export's own
self-checks test popcount relationships and cannot see it. The positive control
caught it by cross-checking the solver's value against an independent
immediate-win computation: **6,668 positions disagreed**, all of them losses.
Running on a subset that passes gravity, balance, subset and that cross-check
gives **0 errors in both directions**.

---

## 2. Can a check that cannot fail detect anything?

**Script:** `experiments/synergy.py`

Instrument detection power, measured on known failures, across the three
families the fleet actually contains.

| instrument | recall |
|---|---:|
| fail-open harness, as measured | **0.000** |
| fail-open harness, 85% instrumented | 0.878 (expected 0.850) |
| fail-open harness, after the one-rule fix | **1.000** |

And the memorisation arm — a dataset whose feature is **pure noise** with
duplicate observations sharing labels:

```
random 80/20 split      balanced acc 1.000   <- perfect, from nothing
group-aware split       balanced acc 0.775
```

**The error I made, twice, and the insight I got wrong twice.** My first leak
model correlated the feature with the label, which just builds a real signal and
reproduced nothing (+0.02 against a real +0.45). My second overwrote random
labels, which is corruption, not leakage. **Both attempts made the feature
informative** — a leaking split's entire crime is leaving the feature
uninformative while making it *look* predictive. Only a model that can
**memorise** expresses the mechanism; a threshold cannot. 1-NN can.

---

## 3. Do chains or forks of models buy independent thinking?

**Data:** `fork_neff.json`, `fork_raw.json`, `refract_neff.json`, `refract_raw.json`
**Method:** 7 free OpenRouter models across 7 vendors, seeded with three real
artifacts from other agents in this fleet (`quilt-in-git`, `jev-net`, `wardroom`).
Outputs embedded with **BGE-M3** via Cloudflare Workers AI, pairwise similarity
matrix, Kish n_eff.

| topology | mean agreement | n_eff of 7 |
|---|---:|---:|
| parallel, one shared prompt | 0.846 | 0.165 |
| chain, each reads the previous | 0.797 | 0.201 |
| fork, round 1 | 0.829 | 0.167 |
| fork, round 2 endpoints | 0.763 | 0.179 |

**I predicted fork would beat chain. It does not.** The difference is inside the
noise of six or seven embeddings and I am not claiming significance for it. They
are the same number.

**What refinement does buy:** inside the fork arm, agreement fell **0.829 →
0.763** when each branch was asked to find the weakest joint in *its own*
answer. **Refinement works. Diversification does not.**

**The consequence, which inverts the usual instinct:** the three seeds produced
genuinely different framings, and it was not because the models differed — it
was because the **material** differed. **Diversity of evidence beats diversity of
opinion** — which is now also the conclusion of experiment 4, and the reason
experiment 4 is a refutation is carefully stated.

---

## 4. Does a quilt gain independence from evidence, or from judges?

**Script:** the quilt arm · **Data:** `quilt_results.json`

Seven cells predicting exact minimax, 6,264 verified positions, scored two ways.

| arm | what varies | n_eff of 7 | mean accuracy |
|---|---|---:|---:|
| **E** | the **evidence** — 7 different observations | **0.17** | 0.8409 |
| **J** | the **judge** — 7 learners, identical evidence | **0.15** | 0.8939 |

**Delta +0.02. Inside the noise. Prediction refuted.**

### The error I made, and it is the worst one

**I used a random 80/20 split.** Every brief I wrote that day said *"the by-ply
split, never the random one."* My own script ignored it, and immediately:

> **L4, the 64-bit irreversible hash, scored 0.9244** — tying the lossless board.

**The same failure I had measured, documented, and pushed, reproduced inside my
own experiment in the same session I wrote it up.** Four instances now, one of
which is mine. This is why the docstring in `synergy.py` keeps its own bugs.

### The genuinely useful result, from the arm that failed

> **L6 — six column heights plus per-column occupancy bits — scored 0.9871,
> beating the lossless 84-column observation at 0.9239.**

Less evidence, better accuracy, because the representation matches the decision.
And **L7 — the squares owned by *both* players, a nearly-empty set — scored
0.5808.** A cell should carry the representation matched to its decision, not
the richest one available.

### The measurement lesson underneath

n_eff computed over *outputs* measures agreement, not independence. Predictions
spanning 0.58 to 0.99 in accuracy still agreed with each other. **Independence is
agreement in the errors** — which is precisely what the budget-matched replication
found when 1-NN memorised a leaking split.

---

## Reproducing any of it

```bash
git clone https://github.com/SuperInstance/fleet-triage.git
cd fleet-triage
python3 experiments/projection_doctrine.py   # 1
python3 experiments/synergy.py               # 2
python3 test_resolver.py                     # the resolver's 14 tests,
                                             # including a negative control
```

Experiment 3 needs `${OPENROUTER_KEY}` and `${CLOUDFLARE_TOKEN}`; experiment 4
needs `connect4`'s ground truth. **`quilt_results.json` and `fork_neff.json` hold
the raw outputs** so the numbers can be re-derived without re-spending the calls.
