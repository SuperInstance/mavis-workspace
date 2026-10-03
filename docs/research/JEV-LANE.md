# JEV-LANE — the continuous probe, made durable

**2026-10-02.** Lane opened because `SuperInstance/jev-quilt` had been reconstructed from
memory roughly fifty times, once per sandbox wipe. The reason was never that the script
was broken. It was that "the script is fine" is a claim about a moment, held in a context
that gets wiped and restated by whoever is next. That is the JEV-contract doctrine applied
to our own tooling: **a recorded interface is a claim about a moment.**

## The deliverable

```bash
git clone https://github.com/SuperInstance/jev-quilt.git && cd jev-quilt
python3 continuous/jev_continuous_probe.py --rounds 1
```

Ten seconds, one command, one checkable number. No key required for the instrument checks.

## What the run prints, and what each line is for

| line | what it proves |
|---|---|
| `CANARY fnv1a_64("café Δ 日本語") = 0x24a555471370b18d [PASS]` | computed, not asserted |
| three `trap ...` lines | the canary is not a constant compared to itself |
| `SEED 20261002` | every verdict is attributable to a draw |
| `TAGS bedrock=9 review=6 arch=5 adversarial=2` | labels are reconciled, not remembered |
| `r001 ... n=k/5 mean_p=... seed=...` | per-round denominator |
| `RUN SUMMARY` block | seed, rounds ok/failed, verdicts obtained/requested, mean with `n=` |
| `EXIT n` | 0 only if the instrument self-tested green **and** every round produced verdicts |

## The canary, and why it is four things

`fnv1a_64` is computed from the **UTF-8 bytes of the NFC form** of `café Δ 日本語` and
compared as an **integer**. Three encodings of the same looking string are computed too,
and each is required to be a *different integer*, so the check cannot pass by construction:

| encoding | digest |
|---|---|
| UTF-8 / NFC — **the canon** | `0x24a555471370b18d` |
| code points / NFC — trap | `0x77ff2029b867f2b5` |
| UTF-8 / NFD — trap | `0x518e6d229c1859ff` |
| UTF-8 / accents stripped — trap | `0xfee91cf40962b966` (measured) |

The previous file carried `0x83ac4441b5e0994` for the last row. **It does not reproduce**
from any obvious spelling, so the code now asserts distinctness only and records what it
actually computed. The canon and the other two reproduce exactly.

Previously the canary existed as *prose* inside `DOCTRINAL_STATE` — a string that said the
canary was pinned, in a file that never computed it. That is a canary comparing a constant
to a constant.

## 1. The label disagreement, canonicalised

Measured from 671 committed rounds, deduplicated; every question drawn 137–172 times.

**Promoted `review` → `bedrock`** (100% hit rate sustained, never promoted in 15+ sessions):

| qid | n | mean_p | hits |
|---|---|---|---|
| `q10_quorum_meshing` | 146 | 0.858 | 146/146 |
| `q17_canary_honesty` | 172 | 0.758 | 172/172 |

**Demoted `review` → `arch`** (0% hit, clean-reject band): `q16` 0.224 · `q19` 0.260 ·
`q21` 0.286 · `q22` 0.335. **Demoted `speculative` → `arch`:** `q06` 0.221.

**Retagged `speculative` → `review`:** `q09` 0.604 · `q11` 0.592 · `q18` 0.586 ·
`q12` 0.557 · `q13` 0.607 · `q20` 0.556. These hit 0% but do not cleanly reject; they sit
in a dead zone and should keep being watched rather than being written off.

**Unchanged:** `q01`–`q05`, `q07`, `q08` (100% hit, 0.878–0.970). `q14`/`q15` stay
`adversarial` — that is a **role**, not a measurement, and both measured 0.066 / 0.191,
i.e. the control group rejects cleanly, as a control must.

**Where the dispatch was wrong, and what was counted instead:** it placed `q20` in the
0.22–0.35 clean-reject band. Measured, `q20` is **0.556** — the dead zone. It is tagged
`review`, not `arch`. The dispatch also said `q16`/`q19`/`q20`/`q21` carry tags saying
`arch`/`review`; in the bank all eight `review` tags read `review`. The rule applied is
`TAG_RULE` in the probe, and `--check` exits non-zero if the bank and the history disagree,
so this cannot silently rot again.

## 2. History — it was FRAGMENTED, not stale

| | |
|---|---|
| history files on the remote | **15** |
| lines read | **671** |
| unique rounds | **671** |
| exact duplicates | **0** |
| local (wiped) history | **80** rounds |
| local ∩ remote | **80** — the local 80 are a strict subset |
| local-only rounds | **0** |
| union | **671** — merging adds nothing, nothing is overwritten |

So the committed history is not behind: every round the wiped sandbox still had was
already on the remote. What is wrong is **layout**: `jev_sessions/history.jsonl` — the
probe's own default `--out` path — holds **2** lines, while **669** rounds sit in
`runs/*/` and `jev_sessions_continuous/*/`. A reader opening the obvious file sees a
2-round history and concludes the fleet has no data. Recorded, not silently overwritten.

## 3. `q10`'s state-leak — fixed, and **NOT verified**

`q10` asks whether five amateur musicians outperform one virtuoso "just by playing louder".
That is a world-knowledge question wearing a canon question's clothes: the answer is
*true* (cf. Page et al. 2014), so the model scores it high whether or not the doctrine
states it. The 0.858 / 100% was measuring familiarity with the analogy.

Fix: a `named-criterion` doctrinal-state entry that names what is being scored
("canon means the doctrine states the claim, not that the claim is true"), plus a reworded
question stem. `--ab-q10` runs the same question under the pre-fix and post-fix state and
reports the delta.

> **This fix is UNVERIFIED.** `TYPESAFEAI_KEY` is absent in this sandbox, so the delta
> could not be measured. I am not claiming it worked. Run:
> `TYPESAFEAI_KEY=... python3 continuous/jev_continuous_probe.py --ab-q10 --rounds 5`

## 4. Transport vs schema

`call_jev` now returns `ok` / `transport-fail` / `schema-fail`, and `classify_failure`
keeps them apart: 502/503/504/529, TLS EOF and timeouts are **transport**; 4xx with a
validation body is **schema**. `validate_spec_shape` checks every spec against
`fleet-triage/JEV-CONTRACT.md` *before* a round is spent — `choice` takes
`criteria:{label:null}`, `score` takes ordered `levels:`, `noul` takes neither.
`parse_distributions` preserves `confidence` and any `probabilities` map; nothing on the
noul path collapses a distribution to a scalar.

## It can go red — demonstrated

```
python3 continuous/jev_continuous_probe.py --inject-fault canary   → 1 check red,  exit 1
python3 continuous/jev_continuous_probe.py --inject-fault nfc      → 3 checks red, exit 1
python3 continuous/jev_continuous_probe.py --inject-fault tag      → 1 check red,   exit 1
python3 continuous/jev_continuous_probe.py --inject-fault parser   → 1 check red,   exit 1
```

And a real edit, not an injected one: changing a single digit of `CANARY_FNV1A64` in a
copy of the file turns `--rounds 1` red and it **refuses to spend a round**:

```
  FAIL  canary: FNV-1a-64 of UTF-8/NFC bytes == 0x24a555471370b18d (computed 0x24a555471370b18d)
INSTRUMENT SELF-TEST RED — refusing to spend rounds on a broken instrument.
```

`python3 continuous/test_probe_kat.py` → **47/47**, including negative controls on the
parser, the canary, and the tag reconciliation.

## The rule

**Never write a count into a narrative before counting it.** A 441-file commit message
once described a commit containing one file, because `git add` timed out on NFS and
committed the partial batch it happened to hold. So: the summary prints its own seed, its
own round count, its own failure count and its own denominator in the same breath as the
mean. A round that did not run is counted as a failure, not skipped. A question that was
not drawn is not in the denominator. A mean over a subset is never printed without its
size.
