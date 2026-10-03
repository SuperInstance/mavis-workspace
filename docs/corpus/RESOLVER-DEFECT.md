# Resolver defect: the line-anchor window propagates one range to every path in a list

Found by orchestrator review, 2026-10-01 06:50Z, while validating SPRINT-1's
`resolver.py` against `superinstance-papers` (6,729 citations / 2,295 documents).

## Verdict

**All 4 `LINE_OOR` findings the tool reports are false positives produced by a
single bug.** The category is empty. The tool reports 73.9% resolution and
26.1% failure; of the failures, 928 `FILE_MISSING` are real, but the
"sharpest category" I cited in the sprint brief — the one I ranked worst — is
**entirely an artifact of the tool.**

I reported that category in the sprint brief and to Casey. I am correcting it
here rather than leaving it standing.

## The mechanism

`resolver.py:329-337`, in `extract_citations`, for a path with no inline `:NN`
anchor (the `` `f.py` (line 437) `` form):

```python
win = text[max(0, m.start() - 140): m.end() + 140]
for pat in LINE_PATTERNS:
    lm = pat.search(win)          # <-- FIRST match in the window
    if lm:
        line_a = int(lm.group("a"))
        ...
        break
```

A **±140 character window** is scanned and the **first** line-number pattern in
it is attached to the path. In a numbered list, that window spans adjacent
items.

## Minimal reproduction

Input, verbatim from `agent-messages/onboarding/build_test_engineer_round6.md:150-155`:

```
3. **Implementation**: `src/gpu/RateBasedChangeEngine.ts` (lines 1-977)
4. **GPU Engine**: `src/gpu/GPUEngine.ts`
5. **Sensation System**: `src/spreadsheet/core/Sensation.ts` (lines 1-580)
```

Attributed anchors, as the tool computes them:

| path | attributed | truth |
|---|---|---|
| `src/gpu/RateBasedChangeEngine.ts` | lines 1-977 | **lines 1-977 — correct, file has 977 lines** |
| `src/gpu/GPUEngine.ts` | lines 1-977 | **no range was ever claimed for this file** |
| `src/spreadsheet/core/Sensation.ts` | lines 1-977 | **lines 1-580, not 1-977** |

`GPUEngine.ts` sits ~150 characters downstream of `(lines 1-977)`, so the
window catches it. `Sensation.ts` gets 977 because `pat.search()` takes the
**first** match, not the nearest.

## Ground truth, measured

```
src/gpu/RateBasedChangeEngine.ts   wc -l=976   real lines=977   (no trailing newline)
src/gpu/GPUEngine.ts               wc -l=598   real lines=599   (no trailing newline)
src/spreadsheet/core/Sensation.ts  wc -l=579   real lines=579   (no trailing newline)
```

`file_line_count` at `resolver.py:403` is **already correct** —
`data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)` handles the
missing trailing newline. My first hypothesis, that the counter was `wc -l`
-naive, was wrong. The counter is right; the **anchor attribution** is wrong.

## Two findings that do survive

1. **`RateBasedChangeEngine.ts` cited as `lines 1-977` — correct.** No defect.
2. **`Sensation.ts` cited as `lines 1-580`, file has 579 — a genuine off-by-one**,
   hidden inside the noise of the propagated 977. This is a real (trivial)
   staleness artifact, and the tool *missed* it while reporting three
   false positives for the same file.

## The fix

Do not search a window. Attribute an anchor only when it is in the **same
clause or list item** as the path:

- bound the window to the current line, or to the current list item
  (`^\s*(\d+\.|[-*])\s` boundary), and take the **nearest** match by character
  distance, not the first
- prefer the **inline** form `` `path:12-14` `` and treat the prose form as
  lower-confidence: emit `PATH_PRECISE_ONLY` or a dedicated
  `ANCHOR_AMBIGUOUS` rather than asserting a line range

## Why this matters more than the count

A claim-resolver whose job is to say *this citation is false* fails at its job
if it says it about a file nobody made a claim about. Every false positive
spends a reader's trust in every true positive, and this fleet has already
established — from the 13 fail-open harnesses, the 8 CRDT ports, and the 6.8×
constant — that the failure mode to fear is **a well-formed, checkable, wrong
artifact with no instrument that can say so**.

This bug *is* that failure mode, inside the instrument built to detect it.

## What is still trustworthy

Unaffected by this bug, and independently reproduced by me:

| outcome | count | share |
|---|---:|---:|
| RESOLVES | 4,970 | 73.9% |
| FILE_MISSING | 928 | 13.8% |
| REPO_UNKNOWN | 314 | 4.7% |
| REPO_NOT_INDEXED | 303 | 4.5% |
| PATH_PRECISE_ONLY | 160 | 2.4% |
| AMBIGUOUS | 45 | 0.7% |
| REPO_MISMATCH | 5 | 0.1% |
| LINE_OOR | 4 | **0.1% — all four are this artifact** |

**928 references in `superinstance-papers` point at files that do not exist.**
That finding stands, and the tool's `evidence` / `check` fields make it
reproducible in ten seconds — which is the standard the instrument was built to
meet, and which it did meet, for the checks that work.
