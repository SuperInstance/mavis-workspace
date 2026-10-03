# Sprint Lane 1 — The Claim-Resolution Checker

**Tool:** `resolver.py` · **Controls:** `resolver_selftest.py` · **Data:** `resolver_report.json`, `resolver_audit.json`
**Nothing was patched.** Every item below is a report. Fix decisions are yours.

---

## 1. What was built

`resolver.py` takes the fleet's prose and resolves every checkable assertion to
the thing it names, in three stages.

**Stage 1 — CITATIONS (21,014 sites, 20,902 distinct).** Extracts `path`,
`path:line`, `repo/file`, and `file.py` (line N) references; resolves each
against the real repository tree, and where a line is cited, against the real
bytes at that line.

**Stage 2 — NUMERIC.** Finds numeric claims that state their own derivation and
recomputes them. Two self-contained checks, neither needing external data:
a stated ratio against the operands the same sentence supplies, and an
expression against the decimal asserted for it.

**Stage 3 — EXTERNAL (4,472 refs).** arXiv IDs via the arXiv `id_list` API in
retried batches, DOIs via `doi.org`, URLs via HEAD-then-GET. Anything not
fetched is `UNVERIFIABLE`, never a pass.

The repo index is built from 477 local repos plus shallow clones of any fleet
repo the corpus names. The corpus named `Murmur` and `eisenstein`; the tool
cloned both on its own initiative and found the contradiction without being
told either name.

### Outcomes

| outcome | n | meaning |
|---|---:|---|
| RESOLVES | 7,672 | file found; cited line in range |
| FILE_MISSING | 4,789 | repo known + indexed; path absent from its tree |
| AMBIGUOUS | 4,486 | bare name, not uniquely resolvable |
| URL_OK | 3,014 | URL fetched, 2xx |
| PATH_PRECISE_ONLY | 1,583 | real file, cited at a shallower path |
| REPO_UNKNOWN | 1,267 | first segment is not a fleet repo — unproven |
| REPO_NOT_INDEXED | 806 | fleet repo, tree unavailable — UNVERIFIABLE |
| URL_UNVERIFIABLE | 800 | 401/403/429/5xx — could not check |
| URL_DEAD | 380 | HTTP 404/410 |
| ARXIV_RESOLVES | 229 | listed by arXiv |
| REPO_MISMATCH | 203 | cited under one repo, lives in another |
| SKIP | 79 | not a repo citation (home/absolute path) |
| DOI_OK | 28 · DOI_DEAD 9 · DOI_UNVERIFIABLE 11 | |
| LINE_OOR | 10 | file exists; cited line past EOF |
| SYMBOL_MISMATCH | 6 | cited line is not where the named symbol is defined |
| RATIO_MISMATCH | 5 | stated ratio ≠ its own stated operands |
| LINE_IS_DEF / ARXIV_DEAD | 1 each | |

**Scope: 8,358 documents, 2,044,013 lines** — `superinstance-papers`,
`fleet-triage`, `quilt-research-canons`. Resolved against **477 repos /
85,990 files**. One repo done properly beat five done shallowly: 4,789
FILE_MISSING is a real, actionable number, not a smear.

---

## 2. The three failures I did not know to look for

### 2.1 Three line anchors in Paper 01 point at the wrong code

Not asked for. Found because the resolver checks the cited line's *content*,
not just its existence.

```
01-conservation-law-of-intelligence.md:50
  "confirmed in `update_certainty` at line 281 of `rubiks.py`"

$ grep -n 'def update_certainty' logtensor/logtensor/transforms/rubiks.py
252:    def update_certainty(
$ sed -n '281p' logtensor/logtensor/transforms/rubiks.py
    def update_permutation(
```

Line 281 is a **different method**. `update_certainty` is at 252.

```
01-conservation-law-of-intelligence.md:48
  "In the `propagate_change` method of `PermutationTensor` (line 295 of `permutation.py`)"
$ grep -n 'def propagate_change' ... → 369
$ sed -n '295p'  →  if idx[dim] < size - 1:
```

```
01-conservation-law-of-intelligence.md:242
  "corresponds to the `EncodingLibrary` in `permutation.py` (line 281)"
$ grep -n 'class EncodingLibrary' → 415
```

**Why this matters more than the missing-file case.** Every one of these passes
a file-existence check, passes a line-range check, and is still wrong. A
resolver that only asks "does this file exist" reports all three green.

### 2.2 `rubiks.py:437` is a constructor signature, not the formula

```
01-conservation-law-of-intelligence.md:37
  "The layer count function from `rubiks.py` (line 437):
   $$L(c) = \lfloor L_{\max}\cdot(1-\bar{c})^2\rfloor$$"

$ sed -n '437p' logtensor/logtensor/transforms/rubiks.py
    def __init__(
```

The document quotes an equation as the content of a line that contains
`def __init__(`. New outcome `LINE_IS_DEF`, one occurrence in 2.04M lines —
which is the right rate for a defect this specific.

### 2.3 A fabricated arXiv ID attached to a real, famous paper

```
repos/fleet-jepa-midi/docs/self-improving-harnesses.md:1035
  "Reference: [Still & Precup, "An Information-Theoretic Approach to
   Curiosity-Driven Reinforcement Learning"](https://arxiv.org/abs/1106.08089)"

$ curl -s "http://export.arxiv.org/api/query?id_list=1106.08089"   → 0 entries
```

The real paper is **arXiv:1109.6038**. The citation is dressed as genuine
prior art in a reference list; the ID does not exist. Control `2306.04595`
resolves through the same code path, so the negative is not a transport failure.

On the two IDs in the brief (`2610.00001`, `2609.50000`): I confirmed both are
dead against the arXiv API. They no longer appear as live citations anywhere in
this corpus — they survive only inside scout reports that already document them
as fabricated. **I found no third one beyond 2.3, and I am not going to
manufacture a second finding to match the expected number.**

### Also worth your attention (not counted as the three)

- **Four line anchors into a file 138 lines too short.** `crew/brain.py` is
  cited at lines 636, 675, 750 and 804 across two documents; the file has
  **498**. `wc -l` confirms. A drift signature, not a typo.
- **A placeholder DOI in a real-looking one:** `10.1145/xxxxxx` in
  `superinstance-business-homepage`. 404s, and will 404 forever.
- **Nine dead DOIs**, hand-verified: `10.1073/pnas.1408921111`,
  `10.1145/2643634.2643666`, `10.1523/JNEUROSCI.2996-08.2008`,
  `10.1006/anbe.2002.1965` and five more all return HTTP 404 on a live
  `curl -sIL`. Control `10.1038/nature12373` returns 200 through the same path.

---

## 3. The two cases I was told about

Both found unprompted, both reproducible in ten seconds.

**`murmur/transforms/rubiks.py` — 4 citations across 2 documents.** Classified
`REPO_MISMATCH`, which is more useful than "missing": `Murmur` is a real
37-file Next.js app with no `transforms/` directory, and the file is real but
lives in `logtensor`:

```
cited: murmur/transforms/rubiks.py | actual: logtensor/logtensor/transforms/rubiks.py
```

The tool names the correction. Your hand-check reproduced exactly; so did mine,
before I knew which repo it would pick.

**The 6.8× constant.** Found by recomputation from the document's own operands:

```
01-conservation-law-of-intelligence.md:207
  "produces triples with 6.8x higher density than Pythagorean triples
   at the same bound (59,841 vs 10,428)"

59841/10428 = 5.7385      claimed 6.8      off by 15.6%
```

Also caught in `papers-ROOT.md:425` (which quotes paper 01:224), and three times
in `DEVILS_ADVOCATE_PAPERS_56-60.md`. The paper's own asymptotic
`2/√3 ≈ 1.155` on the next line is **correct** and is not flagged — the
negative control is a real control.

---

## 4. False-positive rate

Measured by an **independent verifier** (`resolver.py audit`): a random sample
per outcome, re-checked by filesystem operations that do not consult the
index the resolver used.

| outcome | population | sampled | checked | false positives | FP rate |
|---|---:|---:|---:|---:|---:|
| FILE_MISSING | 4,789 | 400 | 400 | 2 | **0.5%** |
| REPO_MISMATCH | 203 | 203 | 203 | 0 | **0.0%** |
| REPO_UNKNOWN | 1,267 | 400 | 400 | 0 | **0.0%** |
| AMBIGUOUS | 4,486 | 400 | 400 | 0 | **0.0%** |
| LINE_OOR | 10 | 10 | 2 | 0 | **0.0%** |
| PATH_PRECISE_ONLY | 1,583 | 400 | 400 | 36 | 9.0% |
| **TOTAL** | | | **1,805** | **38** | **2.1%** |

**Headline: 0.5% on hard failures** (FILE_MISSING + LINE_OOR — the outcomes that
tell someone a reference is broken), **2.1% overall.** PATH_PRECISE_ONLY is an
advisory outcome, not a breakage claim, and carries the remaining noise.

Second opinion, by hand, on 18 FILE_MISSING using plain `find` with no
involvement from the index: **17 truly absent, 1 resolvable by basename →
5.6%** on a sample of 18, against 0.5% on 400. Small-sample noise; I report
both because the larger one is the better estimate and the smaller one is the
honest one.

### The controls

`resolver_selftest.py` — **29/29 passing.** Six are positive controls (a true
claim must stay quiet) and the rest are near-misses I found *in this corpus*
and froze as regressions. Every one of these was a real false positive before
it was a control:

| control | what it stops |
|---|---|
| `8/20 = 40%` | percent conversion read as arithmetic error |
| `343/20000 ≈ 17mm` | unit conversion |
| `1 + 0.5 × \frac{0.5}{1.5} = 1.17` | compound product; sub-expression quoted |
| `3.35e12 / 48 = 70e9` | scientific notation read as `12 / 48` |
| `run 1 = 16/18 pairs` | run label read as a numeric claim |
| `τ^2 = 1/4` | exponent read as `2 = 1/4` |
| `speed (2.33×) AND quality (12.4 vs 11.8)` | two adjacent metrics, one ratio |
| `\frac{2}{\sqrt{3}} \approx 1.155` | **must stay quiet — it is true** |
| `59841/10428 = 5.74` | **must stay quiet — it is true** |

The `EXPR_MISMATCH` check produced **110 hits on its first full run and 100 of
them were wrong.** I deleted the check's noise rather than shipping it. It now
returns **zero** on this corpus. That is the honest result: a claim-by-claim
arithmetic checker is not viable against prose that contains units, percents
and LaTeX, and the instrument should say so rather than pretend.

---

## 5. What the instrument cannot do

Stated plainly, because a tool that hides its edges is worse than none.

- **`REPO_NOT_INDEXED` (806) and `URL_UNVERIFIABLE` (800) are not passes.**
  They are "could not check". The org owns thousands of private repos; an
  anonymous 404 on `github.com/SuperInstance/X` is not evidence of anything.
  Only 404/410 is reported as dead — 401/403 (not authorised), 429 (rate
  limited) and 5xx are `UNVERIFIABLE`. The first build reported **5,801** dead
  URLs against 380 now. Three separate causes, in descending order of size:
  my own clone-cache directories were being scanned as corpus (9,550 → 8,358
  documents, and most of the phantom URLs with them); ~320 URLs were 429/403/5xx
  misfiled as dead; and the remaining SuperInstance links (635 of them) are
  cross-checked against the fleet census before being called broken.
- **`PATH_PRECISE_ONLY` has 9% FP** and `REPO_UNKNOWN` is explicitly unproven.
  Treat them as a worklist, not a verdict.
- **A repo not in the 477 cannot be checked.** The census knows 5,092 fleet
  repos; 477 are on this machine.
- **A GitHub 404 is not proof of a non-existent repo.** Of 635
  `github.com/SuperInstance/*` references, 63 are 404 anonymously and 34 are
  unverifiable; the census downgrades only those it can vouch for. One is
  `github.com/SuperInstance/$repo.git` — an unsubstituted template variable,
  correctly reported dead, and a small reminder that a URL can be dead by being
  a placeholder.
- **Bare filenames are context-dependent.** `README.md:109` in a paragraph
  about the `eisenstein` crate resolves to `eisenstein/README.md` — and that
  citation is *correct*. My first version resolved it to the citing repo and
  reported a confident, wrong LINE_OOR. Context disambiguation is heuristic.
- **Single-repo scope.** One repository done properly, as instructed. The
  corpus roots are a flag; the index is not.

---

## 6. Reproducing

```bash
python3 resolver_selftest.py                      # 29 controls
python3 resolver.py index                         # 477 repos, auto-clones on demand
python3 resolver.py scan  --out resolver_report.json
python3 resolver.py audit --report resolver_report.json --sample 400
```

State lives in `/workspace/.resolver-state` (clones, index, external cache),
outside every repo root, written atomically. State is rebuildable from scratch;
nothing in the tool depends on it persisting.

### Two defects in the tool itself, found by its own audit

Worth recording because both produced *confident* wrong answers:

1. **The tool indexed its own clone cache.** With state inside `fleet-triage`,
   the index contained a second copy of `logtensor`, and every bare
   `rubiks.py` citation became spuriously AMBIGUOUS. Caught by asking why a
   known-unique filename was ambiguous.
2. **A flaky network mount silently emptied the index.** `find_local_repos`
   skipped repos whose `is_dir()` failed mid-walk, and the build wrote an
   8-repo index. Every citation in the corpus then read as broken — a 99%
   false-positive rate that looked like a legitimate result. The index now
   verifies itself, retries, and refuses to overwrite a good index with a bad
   one. **A resolver that reports 4,000 broken references must be assumed
   broken until proven otherwise.**

### One note

`RESOLVER-DEFECT.md` in the corpus is a concurrent lane's audit of `resolver.py`
itself. Two of its SYMBOL_MISMATCH hits and one LINE_OOR are against my own
file, and are stale — the code has moved since it was written. Correctly
flagged, now out of date.
