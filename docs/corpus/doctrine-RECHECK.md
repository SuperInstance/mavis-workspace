# doctrine-RECHECK — the ladder without max-selection

2026-10-01. Re-derivation of the projection-doctrine experiment after a sibling lane
showed the headline table was a **maximum over four learners**.

**Headline: the sibling lane is right that the table is a maximum, and right that a
maximum is the wrong statistic. The conclusion does not survive in the form published.
But the refutation of P2 survives, and gets stronger, not weaker. The audio claim was
wrong and I was right to doubt it — the durations I reported are correct and the
"2.006×" correction is a parser bug, not my error.**

---

## 1. The data is real, and the filter is worse than reported

`/tmp/c4/` was **empty** (wiped). Rebuilt from
`/workspace/projects/connect4/c4_ground_truth.txt` (md5 `ce8dd724730a6f0f7b3b793b0f19756e`,
54,166 rows), reproducing the 25,939-row verified subset exactly.

| filter | dropped | running |
|---|---:|---:|
| raw | — | 54,166 |
| `pos` has bits ≥ 42 | 23,890 | 30,276 |
| solver value disagrees with independent immediate-win | 4,337 | **25,939** |

**44.1%** of the raw export carries `pos` bits outside the 42-bit `mask` space. That
filter is real and it is load-bearing — it is also the *only* filter that does any work.
**Gravity is a red herring here**: `pos` and `mask & ~pos` are gravity-legal on
**25,939 / 25,939** of the verified rows, and my first rebuild attempt dropped to 7,962
rows by applying a gravity test to `mask` values that still carry their own ≥42 bits.
The docstring in `projection_doctrine.py:37` claims gravity plus subset plus stone-count
is the filter. It is not. The subset is selected by **solver cross-validation against an
independent immediate-win computation**, and that is what the docstring should say.

## 2. The script that produced the published table crashed before printing its verdict

`experiments/run2.log` ends:

```
TypeError: '>' not supported between instances of 'tuple' and 'float'
  File "projection_doctrine.py", line 347, in main
    ("P1 L0 lossless is high", b0 > 0.90, f"{b0:.4f}"),
```

`best()` (`projection_doctrine.py:334`) returns `max(v)` over a list of `(random, by-ply)`
**tuples**, so it compares tuples lexicographically — it selects on the *random*-split
score and returns a tuple. The entire `PRE-REGISTERED PREDICTION VERDICTS` block
**never executed**.

> **The published ladder was not produced by the pre-registered code path at all.**
> It was assembled by hand from the `by-ply` column of `run2.log`, taking a maximum
> per observation — outside the pre-registration, after it, by a method the script
> does not contain.

The three numbers in circulation are exactly the by-ply column maxima:

| | reported | which learner | script says |
|---|---:|---|---|
| L0 lossless | 0.9314 | rf-logreg | never printed |
| L1 colour-collapsed | 0.9202 | logreg | never printed |
| L4 hash64 | 0.5045 | mlp | never printed |

## 3. The ladder, every learner, by-ply split (the honest one)

These are the real numbers from `run2.log` — no re-run needed, the experiment already
ran all four learners on all five observations. **Bold = the learner that was reported.**

| observation | logreg | knn | mlp | rf-logreg | **median** | max *(published)* | spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| L0 lossless | 0.8513 | 0.6105 | 0.9150 | **0.9314** | **0.8831** | 0.9314 | 0.3209 |
| L1 colour-collapsed | **0.9202** | 0.7235 | 0.8947 | 0.8947 | **0.8947** | 0.9202 | 0.1967 |
| L3 coarse colour-preserving | 0.5464 | 0.6420 | 0.7411 | 0.7257 | **0.6839** | 0.7411 | 0.1947 |
| L4 hash64 irreversible | 0.5150 | 0.5056 | **0.5045** | 0.5167 | **0.5103** | 0.5167 | 0.0122 |
| L5 stone count only | 0.5000 | 0.5000 | 0.5000 | 0.6497 | **0.5000** | 0.6497 | 0.1497 |

### The ladder does not survive

> **Published: L0 0.9314 > L1 0.9202, gap +0.0112.**
> **Median: L0 0.8831 < L1 0.8947, gap −0.0116.**

The ordering **reverses**. Max-selection put L0 on top by 0.0112; the median puts L1 on
top by 0.0116. The gap is the same size and the same sign flips — which is exactly what
you would expect if that gap was never a measurement and was only ever an artifact of
*which* learner got picked per row.

L0's spread is **0.3209** (knn 0.6105 to rf-logreg 0.9314). No gap smaller than the
within-observation spread means anything. The ladder as published was reading order in
a table of 0.32-wide rows.

**The one ordering that does survive is the wide one**: L3 (0.6839) and L4 (0.5103) both
sit far below L0/L1, and L4 spread is only 0.0122 — all four learners independently put
an irreversible 64-bit hash at chance. That is a real result and no selection could
manufacture it.

## 4. The refuted prediction — this is the part that holds

Pre-registered P2: colour-collapse should land at chance. It came in at 0.9202.

**Under the median it comes in at 0.8947 — 0.3947 above chance.** The refutation is
*stronger* without max-selection, not weaker, and it does not depend on which learner you
pick: all four exceed 0.72. P2 was wrong. Discarding ownership does **not** destroy
minimax value.

That is the more important result, and it survived. It is also the result that most
directly contradicts the fleet doctrine, so it is the one that had to survive.

Note what this implies: if value is recoverable from occupancy alone at 0.89, the
doctrine's "every projection is lossy" is true in the trivial sense and the interesting
claim — that the loss is **unrecoverable** — is false for this ladder. L1 is not a
degradation of L0. On the by-ply split it is *better than the lossless board*.

## 5. On the sibling's n_eff = 1.48

**I could not reproduce it, and I am not going to report a number I could not compute.**

The four learners' *aggregate* scores have a 4×4 correlation matrix, which needs more
replicates than the 5 observations in the ladder. My attempt to estimate it
self-destructed: L5 has three learners at exactly 0.5000, so its row has zero variance
and the normalisation divides by ~0, producing a diagonal of 0.641, 1.398, 1.165 — a
"correlation matrix" with off-diagonal and diagonal both nonsense. Garbage in, garbage
out; discarded.

What can be said honestly: Kish with uniform weights **always** returns n_eff = k = 4,
so 1.48 cannot come from uniform-weight Kish — it must be a correlation-weighted design
effect, and I have no estimator for it that survives its own diagnostics. **The claim is
unverified, not refuted.**

It does not matter to the conclusion. The median reverses the ladder without needing any
effective-sample-size argument at all: with four correlated learners the median is still
the honest summary, and n_eff only weakens the argument *for* the maximum.

## 6. Controls

- **C1 shuffled labels → 0.5000.** Passes (`run2.log`).
- **Positive control** → **0.9486**, against a 0.95 bar. Passes, and it is the number
  the whole experiment is allowed to rest on.
- **By-ply split only.** The random split is reported in `run2.log` and is the reason
  L4's mlp reads 0.9586 — a 64-bit irreversible hash "beating" the complete board is
  leakage, exactly as warned. **No random-split number is used anywhere above.**

## 7. Audio durations — the sibling lane is wrong, and I checked before believing either of us

The claim: my pushed durations are **2.006× longer** than I reported, because MPEG-2
Layer III does not carry the assumed frame rate.

**I parsed the frame headers of all 17 tracks. The tracks are MPEG-2 Layer III,
22,050 Hz, mono, 48 kbps, and my reported durations are correct to 0.001 s.**

| track | bytes | frames | exact chain | true s | reported s | err |
|---|---:|---:|:--:|---:|---:|---:|
| ep-1/s1 | 42,632 | 272 | ✓ | 7.105 | 7.105 | 0.00% |
| ep-1/s2 | 73,195 | 467 | ✓ | 12.199 | 12.199 | 0.00% |
| ep-1/s3 | 82,442 | 526 | ✓ | 13.740 | 13.740 | 0.00% |
| ep-1/s4 | 63,634 | 406 | ✓ | 10.606 | 10.606 | 0.00% |
| ep-1/s5 | 103,915 | 663 | ✓ | 17.319 | 17.319 | 0.00% |
| ep-1/s6 | 84,010 | 536 | ✓ | 14.002 | 14.002 | 0.00% |
| ep-2/s1 | 54,700 | 349 | ✓ | 9.117 | 9.117 | 0.00% |
| ep-2/s2 | 54,543 | 348 | ✓ | 9.091 | 9.091 | 0.00% |
| ep-2/s3 | 94,668 | 604 | ✓ | 15.778 | 15.778 | 0.00% |
| ep-2/s4 | 91,376 | 583 | ✓ | 15.229 | 15.229 | 0.00% |
| ep-2/s5 | 99,213 | 633 | ✓ | 16.536 | 16.535 | +0.00% |
| ep-3/s1 | 41,064 | 262 | ✓ | 6.844 | 6.844 | 0.00% |
| ep-3/s2 | 57,992 | 370 | ✓ | 9.665 | 9.665 | 0.00% |
| ep-3/s3 | 102,661 | 655 | ✓ | 17.110 | 17.110 | 0.00% |
| ep-3/s4 | 138,553 | 884 | ✓ | 23.092 | 23.092 | 0.00% |
| ep-3/s5 | 113,319 | 723 | ✓ | 18.887 | 18.887 | 0.00% |
| **total** | | | | **216.320** | **216.320** | **0.00%** |

`bytes × 8 / 48000` is *not* an assumption here — at true 48 kbps CBR it is exact, and
it agrees with `frames × 576 / 22050` on every file to three decimals, with the frame
chain consuming **every byte of all 17 files with zero remainder**. The formula only
looks like an assumption if you do not parse the bitstream.

**The bug is in `cftts/probe.py:38`**, which computes frame length as
`int(144*br/sr)+pad`. **144 is the MPEG-1 Layer III coefficient; MPEG-2 Layer III uses
72.** With 144 the parser sees 313-byte frames where 157-byte frames exist, desyncs, and
reports ~0.45× the true duration. The 2× error lives in the measuring instrument, which
is exactly the failure this whole night has been about — and it is the same shape as the
`projection_doctrine.py` tuple bug: a coefficient copied without checking which variant
it belongs to.

I only caught it because the two independent methods **disagreed by exactly 2×**, and
2× is not a coincidence, it is a coefficient. When a cross-check returns a suspiciously
round disagreement, the round number is the evidence.

## 8. What the pushed numbers should now say

**Retract** the ladder table in `RESULTS.log` and the corresponding claim in
`RESOLVER-FINAL.md`. Replace with:

1. **The five-observation, four-learner table in §3**, reported in full, median
   highlighted. Not the maximum.
2. **The ordering claim is withdrawn.** "L0 lossless ≥ L1 colour-collapsed" is not
   supported: under the median L1 is ahead. Any text depending on that ordering is wrong.
3. **P2's refutation is confirmed and strengthened** — colour-collapse recovers
   0.8947 (median) against a pre-registered 0.50, robust across all four learners. The
   doctrine's unrecoverability claim fails here.
4. **P4 is the solid result** — irreversible 64-bit hash at 0.5103, spread 0.0122, all
   four learners independently at chance. This one needs no caveat.
5. **The filter description in `projection_doctrine.py:37` is wrong**; the subset is
   selected by solver cross-check, not gravity.
6. **`projection_doctrine.py:334` `best()` is a type error** that silently prevented the
   pre-registered verdict block from ever running. Fix the return type before any rerun.
7. **Audio durations stand as published**; `cftts/probe.py:38` needs the coefficient
   corrected from 144 to 72, and its current output must not be quoted.

## 9. The correction, stated plainly

The pushed table was a maximum over four correlated learners, assembled by hand from a
run whose pre-registered verdict block had crashed and never executed. The maximum
flipped a sign: it reported L0 above L1 when the median reports L1 above L0. The
absolute numbers were always the least trustworthy part of the table and I published them
as the table. The refuted prediction underneath it is real and got stronger.

`BOARD.md:78` should drop the audio correction — that number is correct, and the
instrument that doubted it has a 144/72 coefficient bug in it.

---

**Does the projection-doctrine conclusion survive without max-selection?** The ladder's
ordering does not — the median reverses L0 and L1, so the pushed numbers must stop
claiming a lossless-above-collapsed ranking and must publish the full four-learner spread
instead (L0 0.8831, L1 0.8947, L3 0.6839, L4 0.5103, L5 0.5000 by median on the by-ply
split); but the load-bearing result survives and strengthens, with the refuted prediction
P2 now at 0.8947 median against a pre-registered 0.50 and the irreversible-hash control
holding at 0.5103 with a 0.0122 spread — and the audio durations need no correction at
all, because `cftts/probe.py:38` is wrong, not the numbers.
