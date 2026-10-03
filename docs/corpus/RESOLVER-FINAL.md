# What the resolver actually established — and the four bugs it took to get there

Orchestrator, 2026-10-01. Consolidating SPRINT-1's report with my own review of
`resolver.py`, and correcting three things I said earlier that the tool's own
output overturned.

## The headline

The conservation paper's load-bearing architecture **does not exist in code
anywhere in the namespace** — not in the paper's own repository, not in any
other SuperInstance repo, and not under any spelling.

| artefact | role in the paper | hits in `org:SuperInstance` | in code |
|---|---|---:|---:|
| `AdaptiveLayerController` | Theorem 2.1 | 3 | **0** |
| `PermutationTensor` | §2.1 architecture | 2 | **0** |
| `update_certainty` | cited at `rubiks.py:281` | 1 | **0** |
| `BattenSpline` | the router | 10 | **0** |
| `ConfidenceCascade` | the gates | 74 | 1 |

Every one of the 3, 2, 1, and 10 hits is **prose**, and the prose is inside
`SuperInstance-papers` itself. `PermutationTensor` and `update_certainty` do
exist in the wild — in `moose` (a multiphysics code), `sparse4pinns`
(differentiable PINNs), `open-strawberry` — **none of them ours**.

The paper states a theorem *over an architecture that has no implementation*.
The theorem is not false; it is true of nothing, because its subject is prose.
And its grounding citation, `murmur/transforms/rubiks.py` line 437, points into
a directory that does not exist: `murmur` is a 37-file Next.js app with no
`transforms/` at all.

**The law itself is real.** γ + η = C is genuinely implemented and running. The
paper proves it for an instantiation that was never built.

## The number that propagates

`01-conservation-law-of-intelligence.md:207` claims Eisenstein triples give
**6.8×** higher density than Pythagorean triples. The operands the same
sentence supplies give **5.7385×**.

The identical wrong constant sits in `eisenstein/README.md:25`,
`CONTRIBUTING.md:68`, `src/lib.rs:32`, **and `tests/algebraic_properties.rs:636,688`**
— in a crate with real CI and real property tests — and `01:203` then cites
that crate as its verification.

> A wrong number passed through a passing test suite into a paper as authority.

The resolver's `RATIO_MISMATCH` stage found this **unprompted**, by
recomputing the ratio from the operands the sentence itself provides. It also
flagged a "15× swarm speedup" and a "14.9×" whose operands give `0/3 = 0.0673×`.

## Four bugs, one disease

Every bug in this instrument — mine and the build agent's — has the same shape:

> **A confident, specific, wrong "this resolves / this does not exist."**

| # | bug | symptom | cost |
|---|---|---|---|
| 1 | line-anchor scanned a ±140-char window, first match | one range attributed to every path in a list | 3 of 4 `LINE_OOR` were fiction about files nobody had claimed a line for |
| 2 | path guard ran before the `:NN` anchor was stripped | every `` `path:line` `` silently dropped | never extracted, never checked |
| 3 | no repo-root fallback for doc-relative resolution | `src/core/valuenetwork.ts` reported missing — it exists, in a 174-file `src/core/` | 7 false positives in one file alone |
| 4 | **basename matching across unrelated repos** | `permutation.py` resolved into `sparse4pinns`, someone else's PINN project | reported "the paper cites line 295, symbol is at 234" for a file **we do not have** |

Bug 4 is the one I nearly reported as a finding. The `SYMBOL_MISMATCH` rows for
`01-conservation-law-of-intelligence.md:48,50` *imply* that real files with
`PermutationTensor` and `update_certainty` were located and that the paper's
anchors miss them. They were not located. The resolver found same-named files
in other people's repositories and compared line numbers against them. **The
`SYMBOL_MISMATCH` rows against the conservation paper are false positives.**

The build agent found two more of its own: the tool indexed its own clone cache
(making every bare `rubiks.py` spuriously AMBIGUOUS), and a flaky mount silently
emptied the index, producing a **99% false-positive rate that looked like a
legitimate result**. Its index now verifies itself and refuses to overwrite a
good index with a bad one. Its own summary is the right generalisation:

> **A resolver that reports 4,000 broken references must be assumed broken
> until proven otherwise.**

## Final numbers

`resolver.py` · scope **8,358 documents, 2,044,013 lines** across
`superinstance-papers`, `fleet-triage`, `quilt-research-canons`, resolved
against **477 repos / 85,990 files**.

| stage | outcome | n |
|---|---|---:|
| citations (21,014 sites) | RESOLVES | 7,672 |
| | **FILE_MISSING** | **4,789** |
| | AMBIGUOUS | 4,486 |
| | PATH_PRECISE_ONLY | 1,583 |
| | REPO_UNKNOWN | 1,267 |
| | REPO_NOT_INDEXED (UNVERIFIABLE) | 806 |
| | REPO_MISMATCH | 203 |
| | LINE_OOR / SYMBOL_MISMATCH / RATIO_MISMATCH | 10 / 6 / 5 |
| external (4,472 refs) | URL_OK | 3,014 |
| | URL_UNVERIFIABLE (401/403/429/5xx) | 800 |
| | URL_DEAD (404/410) | 380 |
| | ARXIV_RESOLVES / ARXIV_DEAD | 229 / 1 |
| | DOI_OK / DOI_DEAD / DOI_UNVERIFIABLE | 28 / 9 / 11 |

**4,789 references point at files that do not exist**, resolved against a real
index — that number is actionable rather than a smear. `FILE_MISSING` requires
the repo to be *known and indexed*, which is what makes it trustworthy where
`REPO_UNKNOWN` and `REPO_NOT_INDEXED` are honestly `UNVERIFIABLE`.

## Corrections I owe

1. I called `LINE_OOR` the worst category and ranked it above the rest. **All
   four were tool artifacts.** One survives on a genuine off-by-one
   (`Sensation.ts` cited as `lines 1-580`, file has 579).
2. I reported "6,732 citations, 26.1% unresolved" from a tool that resolves
   73.9%, because I read the outcome key as `OK` when it emits `RESOLVES`, and
   then twice more from a driver calling the wrong method, a string where it
   wanted a `Path`, and a clone directory named `sp` instead of
   `superinstance-papers`. Every wrong number came from my harness, never from
   the tool. That is the finding I most wanted from this sprint, and it is why
   `test_resolver.py` carries a **negative control that reintroduces the old
   window logic and asserts it really did leak 977**.
3. `RESOLVER-DEFECT.md` is now partly **stale**: the build agent extended
   `resolver.py` after I wrote it, so its own line anchors for `resolver.py:329-337`
   and `file_line_count` at 403 now point at 384 and 512. The tool flagged my
   file, correctly, as out of date. That is the tool working.

## What is safe to quote

- The conservation paper's architecture has **no code implementation** in this
  namespace, under any spelling. Independently reproducible via
  `org:SuperInstance` code search on each symbol.
- `murmur/transforms/` does not exist.
- The 6.8× is false; `59841/10428 = 5.7385`.
- 4,789 file references in the corpus do not resolve against a real index.
- 380 URLs are dead, 1 arXiv ID is dead.

## What is not safe to quote

- Any `SYMBOL_MISMATCH` row that resolves into a non-SuperInstance repository.
- The 266 dangling `src/` references as a *defect count* — at least 213 are
  plan sections naming files not yet written, and 2 are template placeholders.
  A dangling path is a defect only when a document claims the work is done.
- The 1,023 `FILE_MISSING` from my narrower run; the tool's wider, better-indexed
  4,789 supersedes it, and both contain bug-3 and bug-4 false positives.
