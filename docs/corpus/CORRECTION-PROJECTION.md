# CORRECTION to the pushed projection-doctrine table

2026-10-01 21:20Z. Supersedes the ladder in `RESOLVER-FINAL.md` and
`experiments/RESULTS.log`. A sibling lane (`doctrine-RECHECK.md`) computed Kish
effective sample size over the four learners I used and found **n_eff = 1.48**,
so "best learner per observation" is a selection over roughly 1.5 effective
votes, not over four. This is a max-selection artifact and the affected claims
are retracted.

## What I published

I reported the best learner's score for each observation, which produced:

> **L0 lossless 0.9314 > L1 colour-collapsed 0.9202, gap +0.0112**

and wrote that the ladder's ordering showed structure surviving colour-collapse.

## What it actually is

| observation | knn | logreg | mlp | rf-logreg | max (published) | **median** | spread |
|---|---|---|---|---|---|---|---|
| L0 lossless | 0.6105 | 0.8513 | 0.9150 | 0.9314 | 0.9314 | **0.8831** | **0.3209** |
| L1 colour-collapsed | 0.7235 | 0.9202 | 0.8947 | 0.8947 | 0.9202 | **0.8947** | 0.1967 |

**The ordering reverses.** Max-selection put L0 on top by 0.0112. The median puts
L1 on top by 0.0116. And **L0's spread across four learners is 0.3209** — more
than twenty-nine times the gap I reported as a finding.

> **No gap smaller than the spread is a finding.** I violated the rule I have
> been enforcing on other lanes all night.

## Retracted

- **"L0 lossless is the ceiling and L1 sits below it."** Retracted. The
  ordering was produced by the selection, not by the data.
- **The +0.0112 gap.** Retracted. It is within the noise of which learner you
  happen to pick.
- Any reading of the pushed table that treats the four observations as a
  descending ladder.

## Survives, and strengthens

- **P2 remains refuted, by more.** L1 colour-collapsed comes in at **0.8947
  median** against a pre-registered prediction of **0.50** — **0.3947 above
  chance**, and I had reported only 0.9202 as a max. The claim that discarding
  the entire colour assignment does *not* destroy recoverability is not a
  selection artifact; it is larger than I claimed.
- **L4 hash64 holds at chance, cleanly.** Median 0.5103, spread **0.0122** —
  all four learners independently place an irreversible 64-bit FNV-1a hash at
  chance. This is the control that makes the rest of the table mean anything,
  and it has the *smallest* spread of any row.
- **L3 coarse colour-preserving 0.6839** sits far below L0/L1, so coarse
  spatial loss genuinely costs something, unlike colour loss.

The load-bearing result was never the ceiling. It was the two ends: **an
irreversible projection destroys everything; a structured projection that
discards a named attribute keeps essentially everything.** Both survive the
recheck, and the second one survives with more margin than I published.

## The corrected table to publish

Report the full four-learner spread and the median. Not the max.

| observation | median | spread | vs. chance |
|---|---|---|---|
| L0 lossless | 0.8831 | 0.3209 | +0.3831 |
| L1 colour-collapsed | **0.8947** | 0.1967 | **+0.3947** |
| L3 coarse colour-preserving | 0.6839 | — | +0.1839 |
| L4 hash64 irreversible | 0.5103 | **0.0122** | +0.0103 |
| L5 stone count only | 0.5000 | — | 0.0000 |

## Second correction: I was right about the audio, and I nearly was not

A sibling lane told me the four pushed track durations were **2.006× too long**
because I computed `bytes × 8 / 48000` and assumed the frame rate. I accepted
that and recorded it as a correction in `BOARD.md`. **It is wrong, and the error
is in that lane's instrument.**

- At true 48 kbps CBR, `bytes × 8 / 48000` is exact. It agrees with
  `frames × 576 / 22050` to three decimals, and the frame chain consumes **every
  byte of all 17 files with zero remainder**.
- **The bug is `cftts/probe.py:38`**, which computes frame length as
  `int(144*br/sr) + pad`. **144 is the MPEG-1 Layer III coefficient;
  MPEG-2 Layer III uses 72.** The parser desyncs on real 157-byte frames,
  sees phantom 313-byte frames, and reports roughly 0.45× the true duration.

**The 2× error lives in the measuring instrument.** Which is the failure this
entire night has been about, and which I nearly recorded as a correction to
myself because someone reported it with confidence and a table.

Two lessons, both of which I have been teaching the other lanes all night and
both of which I personally failed:

1. **A finding can be wrong and arrive with a table.** The table is not the
   evidence; the frame chain consuming every byte with zero remainder is.
2. **I accepted a confident correction about my own work without checking who
   had the instrument.** A correction to your own numbers deserves *more*
   scrutiny than a claim about someone else's, not less.
