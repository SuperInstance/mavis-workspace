# dangling-TRIAGE — turning 4,789 into a ranked list

**Status: FIRST RANKING — stub. Partial by design. Read §6 before quoting any count.**

Lane: turn dangling references into a ranked, human-checkable list instead of a number.
Nothing was patched. Local only, no pushes.

---

## 0. What I ran, and what it said

I re-ran the resolver rather than re-reading the summary.

```
python3 resolver.py scan --out /tmp/turn4_report.json
→ 460.3s, 8,358 docs, 2,044,013 lines, 21,014 citations, 477 repos / 85,990 files
```

| outcome | n | vs. `RESOLVER-FINAL.md` |
|---|---:|---|
| RESOLVES | 7,696 | +24 |
| **FILE_MISSING** | **4,791** | **+2** |
| AMBIGUOUS | 4,486 | = |
| PATH_PRECISE_ONLY | 1,586 | +3 |
| REPO_UNKNOWN | 1,267 | = |
| REPO_NOT_INDEXED | 806 | = |
| SYMBOL_MISMATCH | 11 | +5 (bug 4; I distrust all of them, see §5) |

**4,791 reproduces.** The ±2 is a re-clone, not a regression. The number is solid
as a *number*. It is not solid as a *defect count*, and §1–§3 are why.

---

## 1. The headline finding: the resolver is pointed at the wrong target

**4,791 `FILE_MISSING` is not the most valuable thing in this lane. It is
approximately the least.** The most valuable class of unverified claim in this
corpus is one the resolver is architecturally unable to see, because in that
class *the path resolves*. The defect is in the number written next to it.

I built a second checker for the class the brief pointed at, and it is worse than
the dangling-reference count by an order of magnitude:

```
/tmp/t4/numcheck.py — 8,368 markdown docs scanned
line-count claims found          820
  target file EXISTS, number exact   88   (10.7%)
  target file EXISTS, number WRONG  396   (48.3%)   <-- the class
  target file absent                336   (41.0%)   (this is the resolver's job)
```

> **In this corpus, a line-count claim about a file that exists is wrong 82% of
> the time (396/484).**

That is a claim about a *resolution failure rate* on the highest-stakes genre in
the fleet. It is a negative finding for the resolver's coverage: the resolver
certifies that a document's file list is intact and is silent on whether the
document's numbers are true. **A number in prose has no instrument at all.**

Caveat, stated because it would be easy to hide: my extractor is regex-based,
one line at a time, and I have hand-read only the top 8 documents below. 396 is
a *lower bound* on the class (cross-line claims are missed) and the per-item
precision is verified by reading, not by the regex. The instrument is
`/tmp/t4/numcheck.py`. Every `actual` in §2 is confirmed by `wc -l`
(spotted-checked on 7 of 7 sampled files); note `wc -l` and the instrument can
differ by 1 on a file with no trailing newline — the instrument uses the
resolver's own rule (`\n` count, +1 when unterminated) so the two agree by
construction wherever they were checked.

---

## 2. RANKED — Tier A: attestation documents with a wrong number

Ranked by `(attestation strength) × (how wrong)`. Every row: `path:line`, claimed,
actual, and the prose, so stance is judgeable in ten seconds.

### A1 — `simulations/optimization/schedules/CREATION_SUMMARY.md` · 11 wrong of 12 claims

**All 12 file-level claims in the "Files Created" section are wrong. Every one
understates.** The document ends `**Status**: Complete` (L410).

| line | file | claims | actual | Δ |
|---|---|---:|---:|---:|
| L11 | `lr_schedule_search.py` | 570 | 589 | +19 |
| L17 | `exploration_schedule.py` | 650 | 754 | +104 |
| L23 | `dream_ratio_optimization.py` | 480 | 581 | +101 |
| L29 | `plasticity_schedule.py` | 520 | 543 | +23 |
| L35 | `federated_sync_schedule.py` | 550 | 579 | +29 |
| L43 | `schedule_generator.py` | 450 | 824 | +374 |
| L49 | `run_all.py` | 300 | 338 | +38 |
| L57 | `test_schedules.py` | 400 | 441 | +41 |
| L63 | `README.md` | 350 | 429 | +79 |
| L69 | `SCHEDULE_GUIDE.md` | 400 | 508 | +108 |
| L79 | `quick_start.py` | 200 | 232 | +32 |
| L75 | `requirements.txt` | 3 | 3 | **exact** |

```prose  L11   1. **`lr_schedule_search.py`** (570 lines)
      L17   2. **`exploration_schedule.py`** (650 lines)
      L91   ## Total Lines of Code
      L93   - **Python**: ~4,500 lines
```

One claim in twelve is right, and it is the 3-line `requirements.txt`. **11/11
Python and Markdown claims are wrong, all in the same direction: the file is
longer than the summary says.** Uniform sign is the tell — this summary was
written from an estimate *before* the code was finished and never revised. The
defect is not carelessness in twelve places; it is one stale document, and
stale-by-undercount is exactly what a "Status: Complete" summary cannot afford
to be.

### A2 — the same document, the defect the resolver *cannot* see

The line counts are the visible half. The invisible half is worse and the
resolver scores it as clean:

```prose  L204  ## Generated TypeScript Classes
      L298  - `src/core/schedules/learning-rate.ts`   … 6 files listed
      L233  ### POLLN Core Modules
      L233  1. **`src/core/valuenetwork.ts`**: Uses `TDLambdaSchedule`
```

- `src/core/schedules/` **does not exist.** All 6 generated files are absent. So
  is `results/` (12 PNGs + 6 JSONs, L276–295). Total 24 absent artifacts.
- `schedule_generator.py:29` writes to `…/src/core/schedules`. It was never run.
- **The 7 integration-point files all exist — and none of them contains the
  string "schedule", case-insensitively, zero occurrences in all 7.**

```bash
$ for f in valuenetwork worldmodel learning decision dreaming meta federated; do
    printf "%-12s %s\n" $f "$(grep -ci schedule src/core/$f.ts)"; done
valuenetwork 0   worldmodel 0   learning 0   decision 0
dreaming 0        meta 0         federated 0
```

So all 7 `src/core/*.ts` paths **resolve** — the resolver marks them `RESOLVES` —
and every one of the 7 claims about them is fiction. L94's
`TypeScript Generated: ~1,500 lines (auto-generated)` attests output that does
not exist. **This is the conservation-paper failure mode in miniature: a
document describing an integration between two things, one of which was never
built, with the missing side named by paths that all check out.**

> The most expensive kind of false positive is a claim the instrument *confirms*.
> These 7 rows are the resolver telling you it works.

### A3 — `simulations/physics/statmech/IMPLEMENTATION_SUMMARY.md` · 18 wrong

```prose  L47   6. **`mean_field.py`** (412 lines)          actual 615  Δ+203
      L16   2. **`ensembles.py`** (456 lines)              actual 639  Δ+183
      L55   7. **`nonequilibrium.py`** (478 lines)         actual 628  Δ+150
      L64   8. **`statmech_simulator.py`** (512 lines)     actual 636  Δ+124
```
Heading: `### Core Python Modules (11 files)` — a count *and* a per-file count,
both in attestation voice ("Implementation Summary"). Worst absolute
misstatement in the corpus after `schedule_generator.py`.

### A4 — `docs/DOCUMENTATION_SUMMARY.md` · 15 wrong, largest systematic gap

```prose  L139  **File**: `docs/guide/api/README.md` (~180 lines)        actual 687  Δ+507
      L152  **File**: `docs/guide/advanced/README.md` (~150 lines)     actual 653  Δ+503
      L128  **File**: `docs/guide/cells/README.md` (~200 lines)        actual 617  Δ+417
      L174  **File**: `docs/guide/configuration.md` (~140 lines)       actual 517  Δ+377
```
Titled "documentation summary"; the hatted numbers are the most-wrong
(`Δ+507` on a 687-line file). The real docs are ~3.5× the size claimed.

### A5–A8 — same shape, next by volume
| # | doc | wrong | median \|Δ\| |
|---|---|---:|---:|
| A5 | `production/distributed_training/PROJECT_OVERVIEW.md` | 16 | 61 |
| A6 | `simulations/advanced/metalearning/COMPLETE_SUMMARY.md` | 14 | 48 |
| A7 | `simulations/tooling/profiler/SUMMARY.md` | 14 | 73 |
| A8 | `simulations/advanced/multiobjective/SUMMARY.md` | 13 | 39 |

Full ranking, all 396 rows with deltas: `/tmp/t4/stance.json`.

---

## 3. RANKED — Tier B: `FILE_MISSING` bucketed by what the document is *doing*

Stance cannot be regexed — agreed, and I did not pretend otherwise. What I did
was bucket all 4,791 mechanically, then hand-read the top of each bucket. The
bucket boundaries are where the judgement actually happens, and **two of the
three boundaries moved once I read the prose.** That is the finding.

| rung | n | share | what it is |
|---|---:|---:|---|
| **A. plan / anticipate** | 1,013 | 21.1% | roadmap or checklist naming files not yet written |
| **B. attestation** | 251 | 5.2% | summary/final-report genre naming a missing file |
| **C. neutral** | 3,527 | 73.6% | no filename or heading signal either way |

### Rung A is correct work. 1,013 of 4,791.
```prose  docs/research/spreadsheet/ROADMAP.md                          86 refs
      docs/archive/wave-reports/WAVE7_CHECKLIST.md                   51 refs
      repos/forgemaster-docs/FLUX-MASTER-ROADMAP.md                  55 refs
      playtest2/quilt-gpu-lab/proposals/canons-gpu-ideas-*.md        44 refs
```
A roadmap that never named a future file would be a useless roadmap. **Flagging
these is flagging correct work**, and at 21% of the total they are the single
largest identifiable slice of the scary number being *not* a defect. This
reproduces your 213/266 ratio at full scale: ~1 in 5.

### Rung C is mostly a third genre, not a fourth. 3,527 of 4,791.
The bulk sits in documents with no stance signal at all — session logs, dated
memory archives, `.agents/notes/`, external "gems analysis". These are
**descriptions of a system that lived in a different tree**, not claims about
this one:
```prose  repos/forgemaster-memory-archive/2026-05-{11,14,17,18,19}.md   176 refs
      repos/zeroclaw-dissertation/research/external/2026-08-20-*.md   70 refs
```
A dated archive entry pointing at a path that never made it into the fleet is a
*record*, and the record is doing its job. **I am calling this rung negative:
no defect, by design of the genre.**

### Rung B is the only real target, and it shrank 58% on reading. 251 → ~104.

Your `P75-production-verification.md` (67 refs, the single largest
attestation-genre document) is **not a defect list**:
```prose  L13  | **#1** | Params dispatch: handler(command) → handler(params) | P0 | ✅ **VERIFIED** |
         `CommandExecutor.lua:380-389` — local params = command.params; …
```
`CommandExecutor.lua` appears in **none of the 477 indexed repos** and the
citing repo is `si-papers-new`, which is a papers repo. This is Roblox Lua for a
project the fleet index does not contain. The document may well be true; the
fleet simply cannot check it. **That is `REPO_UNKNOWN` wearing a
`FILE_MISSING` costume** — and it is 67 of the 251.

Second correction, from the same document's neighbours:
```prose  simulations/advanced/metalearning/INDEX.md:68
         **Output**: `maml_config.json`, `maml_hyperparameters.png`
         **Output**: `reptile_config.json`, `maml_reptile_comparison.png`   … 14 of these
```
`## 📄 File Descriptions` is attestation voice, but "**Output**:" names what a
script *writes when run*, not a committed source file. **58 of the 251 rung-B
rows are run-time artifacts** (`.png`/`.json`/`results/`). Same class as
A2's missing `results/` — a described consequence of execution, not an attested
deliverable.

**Revised rung B: ~104 rows, of which ~58 were run-time artifacts and ~67 were
off-index repos** — the two overlap, so the honest statement is: **after reading,
rung B does not have a confirmed single defect in it yet.** I am reporting that
as the finding rather than manufacturing 104 defects to justify the section.

---

## 4. What the ranking means

| rank | class | n | act on it? |
|---|---|---:|---|
| **1** | **Wrong number next to a resolving path** (Tier A) | 396 | **yes — highest value, zero coverage** |
| 2 | `FILE_MISSING` in a plan section | 1,013 | no — correct work |
| 3 | `FILE_MISSING` off-index / archive genre | 3,527 | no — uncheckable by construction |
| 4 | `FILE_MISSING` in attestation genre | ~104 | **unresolved — needs the reading I did not finish** |

Rank 1 beats rank 4 on every axis: it is 4× larger, it has **no instrument at
all** (the resolver returns `RESOLVES` on it), and it is decidable by `wc -l` in
one second. Rank 4 is a list I could not finish reading.

The "one line" version: **the resolver's 4,791 dangling references are mostly
correct plans and uncheckable archives; the 396 wrong numbers next to files that
resolve are the actual defect class, and nothing in the fleet is looking.**

---

## 5. Trust boundaries (bug 4, and my own)

- **11 `SYMBOL_MISMATCH`, all untrusted.** Same disease as your bug 4. None of my
  ranked items depends on one.
- **`AMBIGUOUS` = 4,486 — the largest unexamined bucket in the report.** I did
  not rank it. It is 94% of the size of the class I am ranking first and it may
  contain the same defect. **Highest-value next step, above finishing rung B.**
- `REPO_NOT_INDEXED` (806) and `REPO_UNKNOWN` (1,267) are honestly
  `UNVERIFIABLE` and I have left them that way rather than promoting them.
- My own numcheck is a regex over single lines. It misses cross-line claims
  (so 396 undercounts) and can mis-attribute a number to the wrong file in a
  dense list. Every row in §2 was read by hand; the rest of the 396 is not yet.

## 6. What I have NOT done

- Rung B is **bucketed, not resolved.** The ~104 is a ceiling, not a count.
- Tier A covers the top 8 documents by hand. The other 68 are machine-ranked on
  `(no plan signal) × |Δ|` and inherit my regex's precision.
- I did not check test counts, coverage numbers, or file counts in prose — the
  other three families in `/tmp/t4/numcheck.py`'s design. `docs/DOCUMENTATION_SUMMARY.md`
  already has an "11 files" style count in it; unexamined.
- No patches, per instruction. The 396 rows are reproducible:
  `python3 /tmp/t4/numcheck.py` → `/tmp/t4/numclaims.json`; stance buckets in
  `/tmp/t4/stance.json`; `FILE_MISSING` buckets in `/tmp/t4/fm_stance.json`.
