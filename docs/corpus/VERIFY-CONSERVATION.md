# VERIFY-CONSERVATION — audit of `01-conservation-law-of-intelligence.md`

**Date:** 2026-10-02 · **Scope:** the single claim γ+η=C and the architecture it is stated over.

**Method.** No `${GITHUB_TOKEN}` was available in this environment and `gh` was not installed, so an
authenticated `org:SuperInstance` code search was **not possible** (unauthenticated code search returns
HTTP 401). I instead ran `git clone --depth 1` against the five public repositories the paper names,
and `--unshallow`ed `Murmur` to search its full history. All findings below come from reading and
executing the actual repositories, never from the paper's own prose.

**Note on the account:** `SuperInstance` is a *user* account (Casey Digennaro), not an org, with
**5,127 public repositories**. "Fleet-wide" across 5,127 repos is therefore **not** independently
reproducible without an authenticated code search. My symbol search covers the 5 repos the paper
actually cites. This is a real limit on claim 2 and is stated as such below.

Repos cloned: `SuperInstance-papers`, `Murmur`, `eisenstein`, `batten-spline`, `confidence-cascade`.

---

## Verdicts at a glance

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `murmur` has no `transforms/`; 37-file Next.js app; 0 hits for `transforms/rubiks.py` | **VERIFIED** |
| 2 | All load-bearing symbols are prose-only, fleet-wide | **PARTIALLY FALSE** — true for the PTT, false for BattenSpline and the Confidence Cascade |
| 3 | Cited line number is wrong twice over | **VERIFIED** (and worse than stated) |
| 4 | The law itself is real | **BACKGROUND — but the theorem refutes itself** (see §4) |
| + | The `6.8×` constant | **VERIFIED WRONG, twice over** — and its "verification" cannot fail |

---

## 1. `murmur` has no `transforms/` — **VERIFIED**

`Murmur` is exactly the 37-file Next.js app described.

- `git ls-files | wc -l` → **37**. Confirmed precisely.
- `find -type d -name transforms` → **no results**.
- `find -name "rubiks*" -o -name "permutation*"` → **no results**.
- Total Python files in the repo: **2**, both under `experiments/critical-mass/`
  (`cm2.py`, `critical_mass.py`).

I unshallowed the clone to test the obvious objection — that the directory existed and was deleted:

- Full history: **13 commits**, **42 distinct paths ever tracked**.
- `git log --all --diff-filter=A --name-only | grep -i transform` → **no results**.
- `… | grep -iE "rubiks|permutation"` → **no results**.

`transforms/`, `rubiks.py`, and `permutation.py` have **never existed in this repository at any commit.**

## 3. The citation is wrong — **VERIFIED, and worse than claimed**

The paper cites the same two files at two different line anchors:

| Anchor | Citation | In the paper |
|---|---|---|
| `rubiks.py` | line **437** | L37 — "The layer count function from `rubiks.py` (line 437)" |
| `rubiks.py` | line **281** | L50 — "`update_certainty` at line 281 of `rubiks.py`" |
| `permutation.py` | line **295** | L48 — "in the `propagate_change` method of `PermutationTensor` (line 295)" |
| `permutation.py` | line **281** | L242 — "`EncodingLibrary` in `permutation.py` (line 281)" |

Line **281 is cited for two different files carrying two different symbols.** Since neither file
exists, no anchor can be checked — but the internal collision is verifiable from the paper alone.

**Additional defect not in the brief: the path is given in two mutually exclusive forms, and both
are wrong.**

- Body (L35): `murmur/transforms/permutation.py`, `murmur/transforms/rubiks.py`
- Reference list (L325–326): `murmur/**logtensor**/transforms/…`

`logtensor` appears in neither the repo nor its history. A third variant,
`logtensor/transforms/hgt.py`, is cited in `experiments/01-conservation-law.md:14`. The
citation is unstable across three documents.

## 2. Symbols — **PARTIALLY FALSE; this half needs retracting**

**The PTT symbols are prose-only. Every one, with zero code hits, across all five repos:**

| Symbol | Code hits | Prose hits |
|---|---|---|
| `PermutationTensor` | **0** | 7 |
| `AdaptiveLayerController` | **0** | 5 |
| `EncodingLibrary` | **0** | 5 |
| `propagate_change` | **0** | 6 |
| `pathway_strength` | **0** | 21 |
| `update_certainty` | **0** | 1 |
| `CertainTensor` | **0** | 1 |
| `LayerRemovalGate` | **0** | 1 |

**But two of your four examples are wrong, and they are wrong because the code is real:**

- **`BattenSpline` is genuine code.** `batten-spline/src/batten_spline/spline.py:14` defines
  `class BattenSpline`, with `def learn(` at line 134 — the very method Theorem 4.2's proof invokes.
  **136 code hits.** `CascadeRouter` is likewise real (83 code hits), as is `Nadaraya` (5).
- **The Confidence Cascade is genuine code.** `confidence-cascade/src/confidence-cascade.ts` exists
  and exports `ConfidenceZone`, `sequentialCascade`, `parallelCascade`, `conditionalCascade`,
  `degradationRate`. The file the paper names at L330 **resolves exactly as written.**

Resolving the paper's reference list file-by-file:

```
MISSING   murmur/logtensor/transforms/permutation.py     (L325)
MISSING   murmur/logtensor/transforms/rubiks.py         (L326)
RESOLVES  batten-spline/src/batten_spline/spline.py     (L327)
RESOLVES  batten-spline/src/batten_spline/router.py     (L328)
RESOLVES  batten-spline/src/batten_spline/batten.py     (L329)
RESOLVES  confidence-cascade/src/confidence-cascade.ts  (L330)
RESOLVES  eisenstein/README.md                          (L331)
RESOLVES  batten-spline/tests/test_property_invariants.py (L332)
```

**6 of 8 references resolve. The fabrication is localised — and it is localised precisely on the two
references that carry Theorem 2.3.** This is a sharper finding than "the paper is fabricated": three
quarters of the bibliography is honest, and the quarter that is invented is exactly the part the
conservation theorem is stated over. A reader spot-checking any *other* reference would find a real
file and conclude the paper was sound.

## 4. Background — the theorem refutes its own law

Flagging this because it is deeper than the missing directory. From the paper's own algebra
(L55–L73), with the cited quadratic layer-removal function:

$$\gamma + \eta = \bar c + (1-\bar c)^2 = 1 - \bar c(1-\bar c)$$

This is **not constant**. It ranges over $[3/4,\,1]$. The paper is honest about this — Corollary 2.1
gives the bound and Remark 2.1 calls the deviation "meaningful" — but it is then cited at L319 as
"the conservation law." The paper also notes at L79–81 that a *linear* removal function
$\bar c + (1-\bar c) = 1$ **would** be exactly conserved, and that "the current quadratic removal
function trades exact conservation for faster compute savings."

So the headline is a conservation law whose own theorem bounds the violation at 25%, proved over a
source file that has never existed in the repository it is attributed to. The deviation is the real
result; it is filed as a rounding error. Confirming whether γ+η=C is *implemented* anywhere in the
5,127-repo account would need an authenticated code search and is **UNVERIFIABLE** here.

---

## 5. The `6.8×` constant — **VERIFIED WRONG, TWICE OVER**

### 5a. The arithmetic is wrong on its own operands

```
59,841 / 10,428 = 5.7385        paper claims 6.8      overstated 1.185×
```

A 6.8× ratio would require a numerator of 70,910. The paper's own sentence does not compute its
own ratio.

### 5b. The operands do not come from a matched enumeration

Reproducing the library's exact counting semantics (`EisensteinTriple::all_with_max_norm` in
`eisenstein/src/lib.rs`, same bounds, same perfect-square test, same no-primitive-filter):

- The Pythagorean count **10,428** is real: it occurs at **c ≤ 8528** (all, non-primitive).
- At **that same bound**, the Eisenstein count is **34,366** — not 59,841.

```
bound where pyth_all == 10,428 :  c <= 8528
eisenstein_all AT THAT BOUND   :  34,366
  -> Eisenstein operand overstated 1.74x
  -> TRUE ratio at that bound   :  3.296x      paper claims 6.8x
```

So the claim is wrong twice: the stated ratio is not the ratio of its own operands, **and** the
operands are not drawn from the enumeration they are attributed to. Matched-convention ratios run
5.46× (all/all at B=100) *down* to 3.98× (B=800); primitive/primitive converges to ~1.75×. **No
convention yields 6.8.**

### 5c. The "verification" is a test that cannot fail

The paper cites `batten-spline/tests/test_property_invariants.py` (L332) as "verified mathematical
properties." That file exists, has 25 tests, and contains **no** reference to 6.8, conservation, γ,
or crystallized intelligence. **The cited verification never tests the conservation law.**

The relevant test is in the `eisenstein` crate — `tests/algebraic_properties.rs`. The test is named
`eisenstein_triple_density_advantage` and the 6.8× appears **in a comment**:

```rust
// Eisenstein triples are ~6.8× denser than Pythagorean triples.
// At c ≤ 50, Pythagorean triples: 16 primitive.
let triples = EisensteinTriple::all_with_max_norm(50);
// Just verify we get a healthy count (exact number depends on search)
assert!(triples.len() >= 16, "Should find at least 16 Eisenstein triples …");
```

Three defects in one test:

1. **It asserts a lower bound of 16, not a ratio.** It passes for any count ≥ 16 — including a
   count implying a ratio of 1.0×. A test that cannot distinguish 6.8× from 1.0× cannot verify 6.8×.
2. **Its own comment is wrong.** Primitive Pythagorean triples at c ≤ 50 number **7**, not 16.
   (16 is the count at c ≤ 100.) The bound was probably taken from the wrong table row.
3. **Actual value: 132 triples at c ≤ 50.** The assertion passes with 8× headroom.

Per the repo's own admission — *"exact number depends on search"* — the number was never intended to
be checked. The comment pre-explains its own unfalsifiability.

This is a real CI-enforced crate (`.github/workflows/ci.yml`, `rust-ci.yml`, clippy `-D warnings`).
**Green CI here means the test ran, not that the claim was checked.**

The wrong constant appears in all four locations reported, plus one more:

```
README.md:25                      — "…~6.8× denser … — 59,841 versus 10,428 at the same bound"
CONTRIBUTING.md:68                — "~6.8× denser than Pythagorean triples"
src/lib.rs:32                      — "analogous to Pythagorean triples but ~6.8× denser"
tests/algebraic_properties.rs:636  — module-level comment
tests/algebraic_properties.rs:688  — the "density advantage" test comment
```

`cargo` is not installed in this environment, so the test suite was **not executed**; the 132/7
figures come from a faithful Python reimplementation of the cited Rust routine, read line by line
from `src/lib.rs:428-457`. The assertion's *logic* is self-evident from the source and does not
depend on that reimplementation.

---

## Bottom line

Items 1 and 3 are confirmed: `murmur` has never contained `transforms/`, `rubiks.py`, or
`permutation.py` in any of its 13 commits, and the paper cites line 281 for two different files in
two different files at two different anchors, under two different directory paths, across three
documents. Every PTT symbol is prose-only — 0 code hits, 8 for 8.

Item 2 must be **partially retracted**: `BattenSpline` (136 code hits) and the entire Confidence
Cascade module are real, and 6 of the paper's 8 references resolve to files that exist. The
fabrication is narrower and more deliberate than "prose-only fleet-wide" — it is confined to the
single subsystem that carries the theorem.

The `6.8×` is wrong by arithmetic on its own operands, wrong again once the operands are traced to
a real enumeration (true ratio 3.296×), and defended by a test that asserts `>= 16` and therefore
passes at any ratio whatsoever, citing a Pythagorean count that is wrong at the bound it names.

**Is the conservation paper's theorem stated over something that exists?**
**No — it is stated over `murmur/logtensor/transforms/rubiks.py`, a path that has never existed in any of that repository's 13 commits, and its own algebra shows the quantity is not conserved.**
